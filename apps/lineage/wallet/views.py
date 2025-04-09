from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Wallet, TransacaoWallet
from django.shortcuts import render, redirect
from django.contrib import messages


@login_required
def dashboard_wallet(request):
    wallet, _ = Wallet.objects.get_or_create(usuario=request.user)
    transacoes_query = TransacaoWallet.objects.filter(wallet=wallet).order_by('-created_at')
    
    paginator = Paginator(transacoes_query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'transacoes': page_obj.object_list,
        'page_obj': page_obj,
    })


def transfer_to_server(request):
    if request.method == 'POST':
        # lógica de transferência
        messages.success(request, 'Transferência para o servidor realizada com sucesso.')
        return redirect('wallet:dashboard')
    return render(request, 'wallet/transfer_to_server.html')


def transfer_to_player(request):
    if request.method == 'POST':
        # lógica de transferência
        messages.success(request, 'Transferência para outro jogador realizada com sucesso.')
        return redirect('wallet:dashboard')
    return render(request, 'wallet/transfer_to_player.html')
