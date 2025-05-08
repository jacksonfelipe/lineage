from django.shortcuts import render
from .models import *
from apps.main.home.decorator import conditional_otp_required
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
import random
from decimal import Decimal
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from .services.box_opening import open_box
from .services.box_populate import populate_box_with_items


@conditional_otp_required
def spin_ajax(request):
    if request.user.fichas <= 0:
        return JsonResponse({'error': 'Você não tem fichas suficientes.'}, status=400)

    prizes = list(Prize.objects.all())
    if not prizes:
        return JsonResponse({'error': 'Nenhum prêmio disponível.'}, status=400)

    # Adicione a opção de falha
    fail_chance = 20  # Representa 20% de chance de falhar
    total_weight = sum(p.weight for p in prizes)
    fail_weight = total_weight * (fail_chance / (100 - fail_chance))

    choices = prizes + [None]  # `None` representa a falha
    weights = [p.weight for p in prizes] + [fail_weight]

    chosen = random.choices(choices, weights=weights, k=1)[0]

    # Deduz uma ficha
    request.user.fichas -= 1
    request.user.save()

    if chosen is None:
        return JsonResponse({'fail': True, 'message': 'Você não ganhou nenhum prêmio.'})

    SpinHistory.objects.create(user=request.user, prize=chosen)

    # Certifique-se de que o usuário tenha uma bag
    bag, _ = Bag.objects.get_or_create(user=request.user)

    # Verifica se o item já existe na bag (mesma id + enchant)
    bag_item, created = BagItem.objects.get_or_create(
        bag=bag,
        item_id=chosen.item_id,
        enchant=chosen.enchant,
        defaults={
            'item_name': chosen.name,
            'quantity': 1,
        }
    )

    if not created:
        bag_item.quantity += 1
        bag_item.save()

    return JsonResponse({
        'id': chosen.id,
        'name': chosen.name,
        'item_id': chosen.item_id,
        'enchant': chosen.enchant,
        'rarity': chosen.rarity,
        'image_url': chosen.get_image_url()
    })


@conditional_otp_required
def roulette_page(request):
    prizes = Prize.objects.all()
    prize_data = [{
        'name': prize.name,
        'image_url': prize.get_image_url(),
        'item_id': prize.item_id,
        'enchant': prize.enchant,
        'rarity': prize.rarity
    } for prize in prizes]

    total_spins = SpinHistory.objects.filter(user=request.user).count()
    fichas = request.user.fichas
    last_spin = SpinHistory.objects.filter(user=request.user).order_by('-created_at').first()

    return render(request, 'roulette/spin.html', {
        'prizes': prize_data,
        'fichas': fichas,
        'total_spins': total_spins,
        'last_spin': last_spin,
    })


@conditional_otp_required
def comprar_fichas(request):
    if request.method == 'POST':
        quantidade = int(request.POST.get('quantidade', 0))
        valor_unitario = Decimal('0.10')  # 10 centavos por ficha
        total = valor_unitario * quantidade

        wallet = Wallet.objects.get(usuario=request.user)

        try:
            aplicar_transacao(
                wallet=wallet,
                tipo='SAIDA',
                valor=total,
                descricao=f'Compra de {quantidade} ficha(s)',
                origem='Wallet',
                destino='Sistema de Fichas'
            )
            # Credita as fichas
            request.user.fichas += quantidade
            request.user.save()
            return JsonResponse({'success': True, 'fichas': request.user.fichas})
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)


@conditional_otp_required
def box_dashboard_view(request):
    box_types = BoxType.objects.all()

    return render(request, 'box/dashboard.html', {'box_types': box_types})


@conditional_otp_required
def box_opening_home(request):
    boxes = Box.objects.filter(user=request.user).order_by('-id')
    return render(request, 'box/opening_home.html', {'boxes': boxes})


@conditional_otp_required
def open_box_view(request, box_id):
    try:
        box = Box.objects.get(id=box_id)
    except Box.DoesNotExist:
        messages.warning(request, "Esta caixa não existe. Você pode comprá-la abaixo.")
        return redirect('games:box_user_dashboard')  # Dashboard com todas as BoxType

    if box.user != request.user:
        messages.warning(request, "Essa caixa não pertence a você. Compre uma nova do mesmo tipo.")
        return redirect('games:box_user_dashboard')

    item, error = open_box(request.user, box_id)

    if error:
        messages.warning(request, error)
        return redirect('games:box_user_dashboard')

    return render(request, 'box/result.html', {'item': item})


@conditional_otp_required
def buy_and_open_box_view(request, box_type_id):
    try:
        box_type = BoxType.objects.get(id=box_type_id)
    except BoxType.DoesNotExist:
        messages.error(request, "Tipo de caixa não encontrado.")
        return redirect('games:box_user_dashboard')

    # Aqui você pode verificar saldo, etc., antes de permitir a compra

    box = Box.objects.create(user=request.user, box_type=box_type)
    populate_box_with_items(box)
    return redirect('games:box_user_open_box', box_id=box.id)
