from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet, TransacaoWallet


@login_required
def dashboard_wallet(request):
    wallet, _ = Wallet.objects.get_or_create(usuario=request.user)
    transacoes = TransacaoWallet.objects.filter(wallet=wallet).order_by('-created_at')[:30]

    return render(request, 'wallet/dashboard.html', {
        'wallet': wallet,
        'transacoes': transacoes
    })
