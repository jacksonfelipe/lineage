from .models import *


def aplicar_transacao(wallet, tipo, valor, descricao="", origem="", destino=""):
    if tipo == "SAIDA" and wallet.saldo < valor:
        raise ValueError("Saldo insuficiente.")
    
    if tipo == "ENTRADA":
        wallet.saldo += valor
    elif tipo == "SAIDA":
        wallet.saldo -= valor
    
    wallet.save()

    return TransacaoWallet.objects.create(
        wallet=wallet,
        tipo=tipo,
        valor=valor,
        descricao=descricao,
        origem=origem,
        destino=destino
    )
