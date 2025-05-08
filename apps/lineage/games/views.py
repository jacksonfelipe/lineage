from django.shortcuts import render, redirect
from .models import Prize, SpinHistory
from apps.main.home.decorator import conditional_otp_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import random


@csrf_exempt
@conditional_otp_required
def spin_ajax(request):
    prizes = list(Prize.objects.all())

    if not prizes:
        return JsonResponse({'error': 'Nenhum prêmio disponível.'}, status=400)

    weights = [p.weight for p in prizes]
    chosen = random.choices(prizes, weights=weights, k=1)[0]

    # Salva o histórico
    SpinHistory.objects.create(user=request.user, prize=chosen)

    return JsonResponse({
        'id': chosen.id,  # Certifique-se de incluir o ID
        'name': chosen.name,  # Certifique-se de incluir o nome do prêmio
        'image_url': chosen.get_image_url()  # Passar a URL da imagem, se necessário
    })


@conditional_otp_required
def roulette_page(request):
    prizes = Prize.objects.all()
    # Criar um dicionário para passar os dados dos prêmios (nome e imagem)
    prize_data = [{
        'name': prize.name,
        'image_url': prize.get_image_url()  # Supondo que você tenha esse método no modelo Prize
    } for prize in prizes]

    return render(request, 'roulette/spin.html', {'prizes': prize_data})
