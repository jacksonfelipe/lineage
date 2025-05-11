from .models import *
from apps.main.home.models import ConquistaUsuario
from django.contrib import messages


def entregar_item_para_bag(user, item_id, item_name, quantity=1, enchant=0, request=None):
    bag, _ = Bag.objects.get_or_create(user=user)
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=item_id,
        enchant=enchant,
        defaults={'item_name': item_name, 'quantity': quantity}
    )
    if not created:
        bag_item.quantity += quantity
        bag_item.save()

    if request:
        messages.success(
            request,
            f"🎁 Você recebeu: {item_name} +{enchant} x{quantity}!"
        )


def recompensa_ja_recebida(user, recompensa):
    return RecompensaRecebida.objects.filter(user=user, recompensa=recompensa).exists()


def registrar_recompensa_recebida(user, recompensa):
    RecompensaRecebida.objects.create(user=user, recompensa=recompensa)


def verificar_recompensas_por_nivel(user, level, request=None):
    recompensas = Recompensa.objects.filter(tipo__iexact='NIVEL')
    
    for recompensa in recompensas:
        nivel_recompensa = None
        try:
            nivel_recompensa = int(recompensa.referencia)
        except (ValueError, TypeError):
            continue

        if nivel_recompensa <= level and not recompensa_ja_recebida(user, recompensa):
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)


def verificar_recompensas_por_conquista(user, codigo_conquista, request=None):
    # Verifica se o usuário possui a conquista (1 query)
    if not ConquistaUsuario.objects.filter(usuario=user, conquista__codigo=codigo_conquista).exists():
        return

    # Puxa todas recompensas já recebidas por esse usuário (1 query)
    recompensas_recebidas_ids = set(
        RecompensaRecebida.objects.filter(user=user).values_list('recompensa_id', flat=True)
    )

    # 🎁 Pega todas recompensas do tipo 'CONQUISTA' com essa referência (1 query)
    recompensas = Recompensa.objects.filter(tipo='CONQUISTA', referencia=codigo_conquista)

    # 🎖️ Verifica as recompensas
    for recompensa in recompensas:
        if recompensa.id not in recompensas_recebidas_ids:
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)

    # 🎖️ Verifica as recompensas por quantidade de conquistas (1 query)
    total_conquistas = ConquistaUsuario.objects.filter(usuario=user).count()
    recompensas_qtd = Recompensa.objects.filter(tipo='CONQUISTAS_MULTIPLAS', referencia=str(total_conquistas))

    for recompensa in recompensas_qtd:
        if recompensa.id not in recompensas_recebidas_ids:
            entregar_item_para_bag(
                user,
                item_id=recompensa.item_id,
                item_name=recompensa.item_name,
                quantity=recompensa.quantity,
                enchant=recompensa.enchant,
                request=request
            )
            registrar_recompensa_recebida(user, recompensa)
