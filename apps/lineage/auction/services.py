from django.db import transaction
from .models import Bid
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory


@transaction.atomic
def place_bid(auction, bidder, bid_amount):
    if not auction.is_active:
        raise ValueError("Leilão encerrado.")

    if bid_amount <= auction.starting_bid:
        raise ValueError("O lance deve ser maior que o valor inicial.")

    if auction.current_bid and bid_amount <= auction.current_bid:
        raise ValueError("O lance deve ser maior que o lance atual.")

    wallet = Wallet.objects.select_for_update().get(usuario=bidder)

    if wallet.saldo < bid_amount:
        raise ValueError("Saldo insuficiente.")

    # Devolve o valor do último lance ao último usuário
    if auction.highest_bidder:
        old_wallet = Wallet.objects.select_for_update().get(usuario=auction.highest_bidder)
        aplicar_transacao(
            old_wallet,
            'ENTRADA',
            auction.current_bid,
            f"Devolução de lance no leilão #{auction.id}",
            origem="Leilão"
        )

    # Desconta o valor do novo lance
    aplicar_transacao(
        wallet,
        'SAIDA',
        bid_amount,
        f"Lance no leilão #{auction.id}",
        destino=str(auction.seller)
    )

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
    if auction.is_active:
        raise ValueError("Leilão ainda está ativo.")

    if auction.highest_bidder:
        # Credita o valor ao vendedor
        seller_wallet = Wallet.objects.select_for_update().get(usuario=auction.seller)
        aplicar_transacao(
            seller_wallet,
            'ENTRADA',
            auction.current_bid,
            f"Venda no leilão #{auction.id}",
            origem=str(auction.highest_bidder)
        )

        # Transfere o item para o inventário do comprador
        dest_inventory, _ = Inventory.objects.get_or_create(
            user=auction.highest_bidder,
            character_name="Leilao",
            account_name="Leilao"
        )

        # Move ou cria item no inventário
        dest_item, created = InventoryItem.objects.get_or_create(
            inventory=dest_inventory,
            item_id=auction.item.item_id,
            defaults={'quantity': auction.item.quantity}
        )

        if not created:
            dest_item.quantity += auction.item.quantity
            dest_item.save()

        # Remove item do leilão
        auction.item.delete()

    else:
        # Devolve o item ao vendedor se não houve lances
        seller_inventory, _ = Inventory.objects.get_or_create(
            user=auction.seller,
            character_name="Leilao",
            account_name="Leilao"
        )

        returned_item, created = InventoryItem.objects.get_or_create(
            inventory=seller_inventory,
            item_id=auction.item.item_id,
            defaults={'quantity': auction.item.quantity}
        )

        if not created:
            returned_item.quantity += auction.item.quantity
            returned_item.save()

        auction.item.delete()

    # Marca o leilão como encerrado (sem excluir)
    auction.is_active = False
    auction.save()
