from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Auction
from .services import place_bid, finish_auction


@login_required
def listar_leiloes(request):
    leiloes = Auction.objects.filter(end_time__gt=timezone.now())
    return render(request, 'auction/listar_leiloes.html', {'leiloes': leiloes})


@login_required
def fazer_lance(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.method == 'POST':
        try:
            bid_amount = float(request.POST.get('bid_amount'))
            place_bid(auction, request.user, bid_amount)
            messages.success(request, 'Lance efetuado com sucesso!')
        except ValueError as e:
            messages.error(request, str(e))
        return redirect('auction:listar_leiloes')

    return render(request, 'auction/fazer_lance.html', {'auction': auction})


@login_required
def encerrar_leilao(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.user != auction.seller:
        messages.error(request, 'Você não tem permissão para encerrar este leilão.')
        return redirect('auction:listar_leiloes')

    try:
        finish_auction(auction)
        messages.success(request, 'Leilão encerrado com sucesso.')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('auction:listar_leiloes')
