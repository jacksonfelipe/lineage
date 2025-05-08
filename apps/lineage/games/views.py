from django.shortcuts import render, redirect
from .models import Prize, SpinHistory
from apps.main.home.decorator import conditional_otp_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random
from decimal import Decimal
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao


@conditional_otp_required
def spin_ajax(request):
    if request.user.fichas <= 0:
        return JsonResponse({'error': 'Você não tem fichas suficientes.'}, status=400)

    prizes = list(Prize.objects.all())
    if not prizes:
        return JsonResponse({'error': 'Nenhum prêmio disponível.'}, status=400)

    weights = [p.weight for p in prizes]
    chosen = random.choices(prizes, weights=weights, k=1)[0]

    # Deduz uma ficha
    request.user.fichas -= 1
    request.user.save()

    SpinHistory.objects.create(user=request.user, prize=chosen)

    return JsonResponse({
        'id': chosen.id,
        'name': chosen.name,
        'item_id': chosen.item_id,
        'item_name': chosen.item_name,
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
        'item_name': prize.item_name,
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
