from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Wallet, TransacaoWallet
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import transferir_para_jogador
from decimal import Decimal
from django.contrib.auth import authenticate
from apps.main.home.models import User


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


@login_required
def transfer_to_player(request):
    if request.method == 'POST':
        nome_jogador = request.POST.get('jogador')
        valor = request.POST.get('valor')
        senha = request.POST.get('senha')

        try:
            valor = Decimal(valor)
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('wallet:transfer_to_player')

        # Verificação de limites
        if valor < 1 or valor > 1000:
            messages.error(request, 'Só é permitido transferir entre R$1,00 e R$1.000,00.')
            return redirect('wallet:transfer_to_player')

        # Verificação de senha
        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect('wallet:transfer_to_player')
        
        try:
            destinatario = User.objects.get(username=nome_jogador)
        except User.DoesNotExist:
            messages.error(request, 'Jogador não encontrado.')
            return redirect('wallet:transfer_to_player')

        if destinatario == request.user:
            messages.error(request, 'Você não pode transferir para si mesmo.')
            return redirect('wallet:transfer_to_player')

        wallet_origem, _ = Wallet.objects.get_or_create(usuario=request.user)
        wallet_destino, _ = Wallet.objects.get_or_create(usuario=destinatario)

        try:
            transferir_para_jogador(wallet_origem, wallet_destino, valor)
            messages.success(request, f'Transferência de R${valor:.2f} para {destinatario} realizada com sucesso.')
        except ValueError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Ocorreu um erro inesperado durante a transferência.")

        return redirect('wallet:dashboard')

    return render(request, 'wallet/transfer_to_player.html')
