from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Wallet, TransacaoWallet
from django.shortcuts import render, redirect
from django.contrib import messages
from .utils import transferir_para_jogador
from decimal import Decimal
from django.contrib.auth import authenticate
from apps.main.home.models import User
from django.db import transaction
from .signals import aplicar_transacao
from apps.lineage.server.querys.query_dreamv3 import TransferFromWalletToChar, LineageServices
from apps.lineage.server.database import LineageDB


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


@login_required
def transfer_to_server(request):

    # Verifica conexão com banco do Lineage
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('wallet:transfer_to_server')

    wallet, _ = Wallet.objects.get_or_create(usuario=request.user)
    personagens = []

    # Lista os personagens da conta
    try:
        personagens = LineageServices.find_chars(request.user.username)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    if request.method == 'POST':
        nome_personagem = request.POST.get('personagem')
        valor = request.POST.get('valor')
        senha = request.POST.get('senha')
        COIN_ID = 57  # Ajuste se necessário

        try:
            valor = Decimal(valor)
        except:
            messages.error(request, 'Valor inválido.')
            return redirect('wallet:transfer_to_server')

        if valor < 1 or valor > 1000:
            messages.error(request, 'Só é permitido transferir entre R$1,00 e R$1.000,00.')
            return redirect('wallet:transfer_to_server')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect('wallet:transfer_to_server')

        if wallet.saldo < valor:
            messages.error(request, 'Saldo insuficiente.')
            return redirect('wallet:transfer_to_server')

        # Confirma se o personagem pertence à conta
        print(nome_personagem)
        personagem = TransferFromWalletToChar.find_char(request.user.username, nome_personagem)
        print(personagem)
        if not personagem:
            messages.error(request, 'Personagem inválido ou não pertence a essa conta.')
            return redirect('wallet:transfer_to_server')

        try:
            with transaction.atomic():
                aplicar_transacao(
                    wallet=wallet,
                    tipo="SAIDA",
                    valor=valor,
                    descricao="Transferência para o servidor",
                    origem=request.user.username,
                    destino=nome_personagem
                )

                transfer = TransferFromWalletToChar(
                    char_name=nome_personagem,
                    coin_id=COIN_ID,
                    amount=int(valor)
                )
                transfer.execute()

        except Exception as e:
            messages.error(request, f"Ocorreu um erro durante a transferência: {str(e)}")
            return redirect('wallet:transfer_to_server')

        messages.success(request, f"R${valor:.2f} transferidos com sucesso para o personagem {nome_personagem}.")
        return redirect('wallet:dashboard')

    return render(request, 'wallet/transfer_to_server.html', {
        'wallet': wallet,
        'personagens': personagens,
    })


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
