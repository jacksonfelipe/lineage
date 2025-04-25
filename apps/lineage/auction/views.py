from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Auction
from apps.lineage.inventory.models import InventoryItem
from .services import place_bid, finish_auction
from apps.lineage.inventory.models import Inventory
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.db import transaction

from django.core.serializers.json import DjangoJSONEncoder
import json


@login_required
def listar_leiloes(request):
    leiloes = Auction.objects.filter(end_time__gt=timezone.now())
    return render(request, 'auction/listar_leiloes.html', {'leiloes': leiloes})


@login_required
def fazer_lance(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.method == 'POST':
        bid_amount_str = request.POST.get('bid_amount', '').strip()  # Garantir que não haja espaços extras
        if not bid_amount_str:
            messages.error(request, 'Você precisa informar um valor para o lance.')
            return redirect('auction:fazer_lance', auction_id=auction.id)

        try:
            # Remover vírgulas se houver
            bid_amount_str = bid_amount_str.replace(',', '.')
            bid_amount = Decimal(bid_amount_str)  # Tenta converter para decimal

            # Garantir que current_bid nunca seja None
            current_bid = auction.current_bid if auction.current_bid is not None else auction.starting_bid

            # Verifica se o valor é válido e maior que o lance atual
            if bid_amount <= current_bid:
                messages.error(request, f'O lance precisa ser maior que o lance atual ({current_bid}).')
                return redirect('auction:fazer_lance', auction_id=auction.id)

            with transaction.atomic():
                # Coloca o lance
                place_bid(auction, request.user, bid_amount)

            messages.success(request, 'Lance efetuado com sucesso!')
            return redirect('auction:listar_leiloes')

        except (ValueError, InvalidOperation) as e:
            messages.error(request, f'Valor de lance inválido. Erro: {str(e)}')
            return redirect('auction:fazer_lance', auction_id=auction.id)

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao realizar o lance: {str(e)}')
            return redirect('auction:fazer_lance', auction_id=auction.id)

    return render(request, 'auction/fazer_lance.html', {'auction': auction})


@login_required
def criar_leilao(request):
    inventories = Inventory.objects.filter(user=request.user).prefetch_related('items')

    inventories_data = []
    for inv in inventories:
        items = [
            {
                'item_id': item.item_id,
                'quantity': item.quantity,
                'item_name': item.item_name,
            }
            for item in inv.items.all()
        ]
        inventories_data.append({
            'character_name': inv.character_name,
            'items': items
        })

    if request.method == 'POST':
        try:
            item_id = int(request.POST.get('item_id'))
            quantity = int(request.POST.get('quantity'))
            starting_bid = Decimal(request.POST.get('starting_bid'))
            duration_hours = int(request.POST.get('duration_hours'))
            character_name = request.POST.get('character_name')

            inventory = get_object_or_404(Inventory, user=request.user, character_name=character_name)

            with transaction.atomic():
                item = InventoryItem.objects.get(inventory=inventory, item_id=item_id)
                if item.quantity < quantity:
                    messages.error(request, 'Quantidade insuficiente no inventário.')
                    return redirect('auction:criar_leilao')

                item_name = item.item_name

                item.quantity -= quantity
                if item.quantity == 0:
                    item.delete()
                else:
                    item.save()

                Auction.objects.create(
                    item_id=item_id,
                    item_name=item_name,
                    quantity=quantity,
                    seller=request.user,
                    starting_bid=starting_bid,
                    end_time=timezone.now() + timedelta(hours=duration_hours)
                )

            messages.success(request, 'Leilão criado com sucesso!')
            return redirect('auction:listar_leiloes')

        except InventoryItem.DoesNotExist:
            messages.error(request, 'Item não encontrado no inventário.')
            return redirect('auction:criar_leilao')

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao criar o leilão: {str(e)}')

    context = {
        'inventories': inventories,
        'inventories_json': json.dumps(inventories_data, cls=DjangoJSONEncoder)
    }
    return render(request, 'auction/criar_leilao.html', context)


@login_required
def encerrar_leilao(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.user != auction.seller:
        messages.error(request, 'Você não tem permissão para encerrar este leilão.')
        return redirect('auction:listar_leiloes')

    try:
        with transaction.atomic():
            finish_auction(auction)
        messages.success(request, 'Leilão encerrado com sucesso.')
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('auction:listar_leiloes')


@login_required
def cancelar_leilao(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.user != auction.seller:
        messages.error(request, 'Você não tem permissão para cancelar este leilão.')
        return redirect('auction:listar_leiloes')

    if auction.end_time <= timezone.now():
        messages.error(request, 'Não é possível cancelar um leilão que já terminou.')
        return redirect('auction:listar_leiloes')

    try:
        with transaction.atomic():
            # Devolver os valores dos lances para os usuários
            for bid in auction.bids.all():  # Supondo que exista uma relação `bids` em Auction
                user = bid.user
                amount = bid.amount

                # Aqui você precisará implementar a lógica de devolução do valor ao usuário
                # Exemplo fictício (você pode substituir com seu sistema de moedas ou créditos):
                user.profile.balance += amount
                user.profile.save()

            # Devolver os itens ao vendedor
            inventory, _ = Inventory.objects.get_or_create(user=request.user, character_name=request.POST.get('character_name', ''))
            item, created = InventoryItem.objects.get_or_create(inventory=inventory, item_id=auction.item_id, defaults={
                'quantity': auction.quantity,
                'item_name': auction.item_name
            })
            if not created:
                item.quantity += auction.quantity
                item.save()

            # Cancelar o leilão
            auction.delete()

            messages.success(request, 'Leilão cancelado e recursos devolvidos com sucesso.')

    except Exception as e:
        messages.error(request, f'Ocorreu um erro ao cancelar o leilão: {str(e)}')

    return redirect('auction:listar_leiloes')

