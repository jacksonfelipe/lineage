from .validators import registrar_validador
from django.utils.translation import get_language_from_request

from apps.main.home.models import AddressUser
from apps.main.solicitation.models import Solicitation
from apps.main.message.models import Friendship

from apps.lineage.shop.models import ShopPurchase, Cart
from apps.lineage.auction.models import Bid, Auction
from apps.lineage.payment.models import PedidoPagamento, Pagamento
from apps.lineage.wallet.models import TransacaoWallet
from apps.lineage.inventory.models import InventoryItem, InventoryLog


@registrar_validador('primeiro_login')
def primeiro_login(user, request=None):
    return True  # Apenas logar

@registrar_validador('10_leiloes')
def dez_leiloes(user, request=None):
    return user.auctions.count() >= 10

@registrar_validador('primeira_solicitacao')
def primeira_solicitacao(user, request=None):
    return Solicitation.objects.filter(user=user).exists()

@registrar_validador('avatar_editado')
def avatar_editado(user, request=None):
    return bool(getattr(user, 'avatar', None))

@registrar_validador('endereco_cadastrado')
def endereco(user, request=None):
    return AddressUser.objects.filter(user=user).exists()

@registrar_validador('email_verificado')
def email_verificado(user, request=None):
    return getattr(user, 'is_email_verified', False)

@registrar_validador('2fa_ativado')
def dois_fatores(user, request=None):
    return getattr(user, 'is_2fa_enabled', False)

@registrar_validador('idioma_trocado')
def idioma(user, request=None):
    if not request:
        return False
    idioma = get_language_from_request(request)
    return idioma != 'pt-br'  # ou qualquer padrão

@registrar_validador('primeiro_amigo')
def primeiro_amigo(user, request=None):
    return Friendship.objects.filter(user=user).exists()

@registrar_validador('primeiro_amigo_aceito')
def primeiro_amigo_aceito(user, request=None):
    return Friendship.objects.filter(user=user, accepted=True).exists()

@registrar_validador('primeira_compra')
def primeira_compra(user, request=None):
    return ShopPurchase.objects.filter(user=user).exists()

@registrar_validador('primeiro_lance')
def primeiro_lance(user, request=None):
    return Bid.objects.filter(bidder=user).exists()

@registrar_validador('primeiro_cupom')
def primeiro_cupom(user, request=None):
    return Cart.objects.filter(user=user, promocao_aplicada__isnull=False).exists()

@registrar_validador('primeiro_pedido_pagamento')
def primeiro_pedido_pagamento(user, request=None):
    return PedidoPagamento.objects.filter(usuario=user).exists()

@registrar_validador('primeiro_pagamento_concluido')
def primeiro_pagamento_concluido(user, request=None):
    return Pagamento.objects.filter(usuario=user, status='approved').exists()

@registrar_validador('primeira_transferencia_para_o_jogo')
def primeira_transferencia_para_o_jogo(user, request=None):
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para o servidor"
    ).exists()

@registrar_validador('primeira_transferencia_para_jogador')
def primeira_transferencia_para_jogador(user, request=None):
    return TransacaoWallet.objects.filter(
        wallet__usuario=user,
        tipo="SAIDA",
        descricao__icontains="Transferência para jogador"
    ).exists()

@registrar_validador('primeira_retirada_item')
def primeira_retirada_item(user, request=None):
    return InventoryItem.objects.filter(inventory__user=user).exists()

@registrar_validador('primeira_insercao_item')
def primeira_insercao_item(user, request=None):
    return InventoryLog.objects.filter(user=user, acao='INSERIU_NO_JOGO').exists()

@registrar_validador('primeira_troca_itens')
def primeira_troca_itens(user, request=None):
    return InventoryLog.objects.filter(user=user, acao='TROCA_ENTRE_PERSONAGENS').exists()

@registrar_validador('nivel_10')
def nivel_10(user, request=None):
    try:
        perfil = user.perfilgamer
        return perfil.level >= 10
    except:
        return False

@registrar_validador('50_lances')
def cinquenta_lances(user, request=None):
    return Bid.objects.filter(bidder=user).count() >= 50

@registrar_validador('primeiro_vencedor_leilao')
def primeiro_vencedor_leilao(user, request=None):
    return Auction.objects.filter(highest_bidder=user, status='finished').exists()

@registrar_validador('1000_xp')
def mil_xp(user, request=None):
    try:
        perfil = user.perfilgamer
        # Calcula XP total acumulado
        xp_total = perfil.xp
        level_atual = perfil.level
        
        # Adiciona XP de todos os níveis anteriores
        for nivel in range(1, level_atual):
            xp_total += 100 + (nivel - 1) * 25
            
        return xp_total >= 1000
    except:
        return False
