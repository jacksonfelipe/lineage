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
            f"🎁 Você recebeu: <strong>{item_name} +{enchant} x{quantity}</strong>!"
        )


def verificar_recompensas_por_nivel(user, level, request=None):
    recompensas = Recompensa.objects.filter(tipo='NIVEL', referencia=str(level))
    for recompensa in recompensas:
        entregar_item_para_bag(
            user,
            item_id=recompensa.item_id,
            item_name=recompensa.item_name,
            quantity=recompensa.quantity,
            enchant=recompensa.enchant,
            request=request
        )


def verificar_recompensas_por_conquista(user, codigo_conquista, request=None):
    recompensas = Recompensa.objects.filter(tipo='CONQUISTA', referencia=codigo_conquista)
    for recompensa in recompensas:
        entregar_item_para_bag(
            user,
            item_id=recompensa.item_id,
            item_name=recompensa.item_name,
            quantity=recompensa.quantity,
            enchant=recompensa.enchant,
            request=request
        )

    total_conquistas = ConquistaUsuario.objects.filter(usuario=user).count()
    recompensas_qtd = Recompensa.objects.filter(tipo='CONQUISTAS_MULTIPLAS', referencia=str(total_conquistas))
    for recompensa in recompensas_qtd:
        entregar_item_para_bag(
            user,
            item_id=recompensa.item_id,
            item_name=recompensa.item_name,
            quantity=recompensa.quantity,
            enchant=recompensa.enchant,
            request=request
        )
