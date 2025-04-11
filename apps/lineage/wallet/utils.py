from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .signals import aplicar_transacao


def transferir_para_jogador(wallet_origem, username_destino, valor, descricao="Transferência entre jogadores"):
    if wallet_origem.usuario.username == username_destino:
        raise ValueError("Você não pode transferir para si mesmo.")

    try:
        usuario_destino = User.objects.get(username=username_destino)
        wallet_destino = Wallet.objects.get(usuario=usuario_destino)
    except ObjectDoesNotExist:
        raise ValueError("Usuário de destino não encontrado.")

    if wallet_origem.saldo < valor:
        raise ValueError("Saldo insuficiente para transferência.")

    with transaction.atomic():
        # Debita da carteira de origem
        aplicar_transacao(
            wallet=wallet_origem,
            tipo="SAIDA",
            valor=valor,
            descricao=descricao,
            origem=wallet_origem.usuario.username,
            destino=wallet_destino.usuario.username
        )

        # Credita na carteira de destino
        aplicar_transacao(
            wallet=wallet_destino,
            tipo="ENTRADA",
            valor=valor,
            descricao=descricao,
            origem=wallet_origem.usuario.username,
            destino=wallet_destino.usuario.username
        )
