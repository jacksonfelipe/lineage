from apps.lineage.server.models import Apoiador, Comissao
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import TransacaoWallet
from decimal import Decimal
from apps.lineage.shop.models import ShopPurchase, PromotionCode
from django.db.models import Sum


def pagar_comissao(apoiador: Apoiador, valor: Decimal):
    # Verificar se a comissão já foi paga para alguma compra associada ao apoiador
    compras_nao_pagas = ShopPurchase.objects.filter(apoiador=apoiador).exclude(comissao__pago=True)
    
    # Se não houver comissões não pagas, retornamos sem fazer nada
    if not compras_nao_pagas:
        return

    # Registra as comissões para as compras não pagas
    for compra in compras_nao_pagas:
        # Criar a comissão
        comissao = Comissao.objects.create(
            apoiador=apoiador,
            compra=compra,
            valor=valor,
            pago=True  # Marca como pago
        )

        # Atualizar a compra para indicar que a comissão foi paga
        compra.comissao_registrada = True
        compra.save()

        # Atualiza a carteira do apoiador
        wallet, created = Wallet.objects.get_or_create(usuario=apoiador.user)
        wallet.saldo += valor  # Adiciona o valor da comissão
        wallet.save()

        # Registra a transação na carteira
        TransacaoWallet.objects.create(
            wallet=wallet,
            tipo='ENTRADA',
            valor=valor,
            descricao='Comissão por venda',
            origem='Sistema',
            destino=apoiador.nome_publico
        )


def calcular_valor_disponivel(apoiador):
    # Tentar pegar o cupom ativo do apoiador
    try:
        cupom = PromotionCode.objects.get(apoiador=apoiador, ativo=True)
        percentual_comissao = cupom.desconto_percentual
    except PromotionCode.DoesNotExist:
        # Se não houver cupom ativo, utilizar um percentual padrão
        percentual_comissao = Decimal('10.0')

    # Total de vendas associadas ao apoiador (com tratamento de None)
    compras_nao_pagas = ShopPurchase.objects.filter(apoiador=apoiador).exclude(comissao__pago=True)
    total_vendas = compras_nao_pagas.aggregate(
        total=Sum('total_pago')
    )['total'] or Decimal('0.00')

    # Calcular comissão gerada com base nas vendas e no percentual do cupom
    comissao_gerada = (total_vendas * percentual_comissao) / Decimal('100')

    # Total já pago (comissões já pagas)
    total_pago = Comissao.objects.filter(
        apoiador=apoiador,
        pago=True
    ).aggregate(
        total=Sum('valor')
    )['total'] or Decimal('0.00')

    # Valor disponível é a comissão gerada menos o total já pago
    valor_disponivel = comissao_gerada - total_pago

    # Garantir que o valor disponível nunca seja negativo
    return max(valor_disponivel, Decimal('0.00'))
