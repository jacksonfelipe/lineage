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

import time


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



@registrar_validador('100_transacoes')
def cem_transacoes(user, request=None):
    from apps.lineage.wallet.models import TransacaoWallet, TransacaoBonus
    # Conta transações normais e de bônus
    transacoes_normais = TransacaoWallet.objects.filter(wallet__usuario=user).count()
    transacoes_bonus = TransacaoBonus.objects.filter(wallet__usuario=user).count()
    return (transacoes_normais + transacoes_bonus) >= 100

@registrar_validador('primeiro_bonus')
def primeiro_bonus(user, request=None):
    from apps.lineage.wallet.models import TransacaoBonus
    return TransacaoBonus.objects.filter(wallet__usuario=user, tipo='ENTRADA').exists()

@registrar_validador('nivel_25')
def nivel_25(user, request=None):
    try:
        perfil = user.perfilgamer
        return perfil.level >= 25
    except:
        return False

@registrar_validador('primeira_solicitacao_resolvida')
def primeira_solicitacao_resolvida(user, request=None):
    from apps.main.solicitation.models import Solicitation
    return Solicitation.objects.filter(user=user, status='closed').exists()

@registrar_validador('primeiro_personagem')
def primeiro_personagem(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens no servidor
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('primeiro_clan')
def primeiro_clan(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens em clãs
        characters_in_clan = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND clanid > 0",
            {"account": user.username}
        )
        return characters_in_clan and characters_in_clan[0]['count'] > 0
    except:
        return False

@registrar_validador('primeiro_castle')
def primeiro_castle(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens em clãs que possuem castelos
        castle_characters = db.select("""
            SELECT COUNT(*) as count 
            FROM characters c 
            JOIN clan_data cd ON c.clanid = cd.clan_id 
            WHERE c.account_name = :account AND cd.hasCastle = 1
        """, {"account": user.username})
        return castle_characters and castle_characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_nivel_50')
def personagem_nivel_50(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND base_level >= 50",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_nivel_80')
def personagem_nivel_80(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND base_level >= 80",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_nobless')
def personagem_nobless(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND nobless = 1",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_hero')
def personagem_hero(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND hero_end > :current_time",
            {"account": user.username, "current_time": int(time.time() * 1000)}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('primeiro_subclass')
def primeiro_subclass(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND (subclass1 > 0 OR subclass2 > 0 OR subclass3 > 0)",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_pvp_100')
def personagem_pvp_100(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND pvpkills >= 100",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_pvp_500')
def personagem_pvp_500(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND pvpkills >= 500",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_pvp_1000')
def personagem_pvp_1000(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND pvpkills >= 1000",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('primeiro_ally')
def primeiro_ally(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND ally_id > 0",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_online_24h')
def personagem_online_24h(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND onlinetime >= 86400",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_online_100h')
def personagem_online_100h(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND onlinetime >= 360000",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_online_500h')
def personagem_online_500h(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # 500 horas = 1.800.000.000 milissegundos
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND onlinetime >= 1800000000",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('olympiad_participant')
def olympiad_participant(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens que participaram da Olimpíada
        characters = db.select(
            "SELECT COUNT(*) as count FROM oly_nobles ON JOIN characters C ON C.obj_Id = ON.char_id WHERE C.account_name = :account",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('olympiad_winner')
def olympiad_winner(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens que venceram batalhas na Olimpíada
        # Vencedores têm pontos positivos na Olimpíada
        characters = db.select(
            "SELECT COUNT(*) as count FROM oly_nobles ON JOIN characters C ON C.obj_Id = ON.char_id WHERE C.account_name = :account AND ON.points_current > 0",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('grandboss_killer')
def grandboss_killer(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens que participaram de kills de Grand Bosses
        # Esta é uma aproximação baseada em kills PvP altas (indicativo de participação em raids)
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND pvpkills >= 50",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('siege_participant')
def siege_participant(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        # Verifica se o usuário tem personagens em clãs que participaram de cercos
        characters = db.select("""
            SELECT COUNT(*) as count 
            FROM characters C 
            JOIN clan_data CD ON C.clanid = CD.clan_id 
            JOIN siege_clans SC ON CD.clan_id = SC.clan_id 
            WHERE C.account_name = :account
        """, {"account": user.username})
        return characters and characters[0]['count'] > 0
    except:
        return False

@registrar_validador('personagem_nivel_100')
def personagem_nivel_100(user, request=None):
    from apps.lineage.server.database import LineageDB
    try:
        db = LineageDB()
        if not db.is_connected():
            return False
        
        characters = db.select(
            "SELECT COUNT(*) as count FROM characters WHERE account_name = :account AND base_level >= 100",
            {"account": user.username}
        )
        return characters and characters[0]['count'] > 0
    except:
        return False
