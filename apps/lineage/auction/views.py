from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Auction
from .services import place_bid, finish_auction
from apps.lineage.inventory.models import Inventory, InventoryItem
from datetime import timedelta
from decimal import Decimal, InvalidOperation
from django.db import transaction


@login_required
def listar_leiloes(request):
    leiloes = Auction.objects.filter(end_time__gt=timezone.now())
    return render(request, 'auction/listar_leiloes.html', {'leiloes': leiloes})


@login_required
def fazer_lance(request, auction_id):
    auction = get_object_or_404(Auction, id=auction_id)

    if request.method == 'POST':
        bid_amount_str = request.POST.get('bid_amount')
        if not bid_amount_str:
            messages.error(request, 'Você precisa informar um valor para o lance.')
            return redirect('auction:fazer_lance', auction_id=auction.id)

        try:
            bid_amount = Decimal(bid_amount_str)

            with transaction.atomic():
                # Só realiza o lance, que já faz a transação no services
                place_bid(auction, request.user, bid_amount)

            messages.success(request, 'Lance efetuado com sucesso!')
            return redirect('auction:listar_leiloes')

        except (ValueError, InvalidOperation):
            messages.error(request, 'Valor de lance inválido. Por favor, insira um número válido.')
            return redirect('auction:fazer_lance', auction_id=auction.id)

        except Exception as e:
            messages.error(request, f'Ocorreu um erro ao realizar o lance: {str(e)}')
            return redirect('auction:fazer_lance', auction_id=auction.id)

    return render(request, 'auction/fazer_lance.html', {'auction': auction})


@login_required
def criar_leilao(request):
    if request.method == 'POST':
        item_id = int(request.POST.get('item_id'))
        quantity = int(request.POST.get('quantity'))
        starting_bid = Decimal(request.POST.get('starting_bid'))
        duration_hours = int(request.POST.get('duration_hours'))

        inventory = get_object_or_404(Inventory, user=request.user, character_name=request.POST.get('character_name'))

        try:
            with transaction.atomic():
                item = InventoryItem.objects.get(inventory=inventory, item_id=item_id)
                if item.quantity < quantity:
                    messages.error(request, 'Quantidade insuficiente no inventário.')
                    return redirect('auction:criar_leilao')

                # Remove o item do inventário
                item.quantity -= quantity
                if item.quantity == 0:
                    item.delete()
                else:
                    item.save()

                # Cria o leilão
                Auction.objects.create(
                    item=item,
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

    inventories = Inventory.objects.filter(user=request.user)
    context = {
        'inventories': inventories
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
