from django.utils import timezone
from django.db import transaction
from .models import Auction, Bid
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory


@transaction.atomic
def place_bid(auction, bidder, bid_amount):
    if not auction.is_active():
        raise ValueError("Leilão encerrado.")

    if bid_amount <= auction.starting_bid:
        raise ValueError("O lance deve ser maior que o valor inicial.")

    if auction.current_bid and bid_amount <= auction.current_bid:
        raise ValueError("O lance deve ser maior que o lance atual.")

    wallet = Wallet.objects.get(usuario=bidder)

    if wallet.saldo < bid_amount:
        raise ValueError("Saldo insuficiente.")

    # Devolve o valor do último lance ao último usuário
    if auction.highest_bidder:
        old_wallet = Wallet.objects.get(usuario=auction.highest_bidder)
        aplicar_transacao(old_wallet, 'ENTRADA', auction.current_bid, "Devolução de lance", origem="Leilão")

    # Desconta o valor do novo lance
    aplicar_transacao(wallet, 'SAIDA', bid_amount, "Lance em leilão", destino=str(auction.seller))

    # Atualiza o leilão
    auction.current_bid = bid_amount
    auction.highest_bidder = bidder
    auction.save()

    # Registra o lance
    return Bid.objects.create(
        auction=auction,
        bidder=bidder,
        amount=bid_amount
    )


@transaction.atomic
def finish_auction(auction):
    if auction.is_active():
        raise ValueError("Leilão ainda ativo.")

    if auction.highest_bidder:
        seller_wallet = Wallet.objects.get(usuario=auction.seller)
        aplicar_transacao(seller_wallet, 'ENTRADA', auction.current_bid, "Venda em leilão", origem=str(auction.highest_bidder))

        # Transfere o item pro inventário do comprador
        dest_inventory, _ = Inventory.objects.get_or_create(user=auction.highest_bidder, character_name="Leilao", account_name="Leilao")
        item = auction.item
        item.inventory = dest_inventory
        item.save()

    auction.delete()  # Remove o leilão
