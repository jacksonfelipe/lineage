def pagar_comissao(apoiador: Apoiador, valor: Decimal):
    wallet, created = Wallet.objects.get_or_create(usuario=apoiador.user)
    wallet.saldo += valor
    wallet.save()
    TransacaoWallet.objects.create(
        wallet=wallet,
        tipo='ENTRADA',
        valor=valor,
        descricao='Comissão por venda',
        origem='Sistema',
        destino=apoiador.nome_publico
    )