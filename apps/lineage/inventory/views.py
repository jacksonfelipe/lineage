from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.contrib.auth import authenticate

from django.db.models import Sum
from .utils.items import get_itens_json

from .models import Inventory, InventoryItem, BlockedServerItem
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class
from django.core.paginator import Paginator

TransferFromWalletToChar = get_query_class("TransferFromWalletToChar")
TransferFromCharToWallet = get_query_class("TransferFromCharToWallet")
LineageServices = get_query_class("LineageServices")


@login_required
def retirar_item_servidor(request):
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('inventory:inventario_dashboard')

    personagens = []
    try:
        personagens = LineageServices.find_chars(request.user.username)
    except:
        messages.warning(request, 'Não foi possível carregar seus personagens agora.')

    char_id = request.GET.get('char_id') or request.POST.get('char_id')
    page_number = request.GET.get('page')
    items = []
    personagem = None

    if char_id:
        try:
            personagem = TransferFromCharToWallet.find_char(request.user.username, char_id)
            if not personagem:
                messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
                return redirect('inventory:retirar_item')

            if personagem[0]['online'] != 0:
                messages.error(request, 'O personagem precisa estar offline.')
                return redirect('inventory:retirar_item')

            all_items = TransferFromCharToWallet.list_items(char_id)

            itens_data = get_itens_json

            # Substitui item_id pelo item_name
            for item in all_items:
                item_id_str = str(item['item_type'])
                item_name = itens_data.get(item_id_str, [f"(não identificado - {item_id_str})"])[0]
                item['name'] = item_name

            paginator = Paginator(all_items, 10)  # 10 itens por página
            items = paginator.get_page(page_number)

        except Exception as e:
            messages.error(request, f'Erro ao buscar o inventário: {str(e)}')

    if request.method == 'POST' and char_id:
        item_id = int(request.POST.get('item_id').replace(',', '').replace('.', ''))
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))
        senha = request.POST.get('senha')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect(f"{request.path}?char_id={char_id}")

        # --- Validação: Item Bloqueado? ---
        blocked_item = BlockedServerItem.objects.filter(item_id=item_id).first()
        if blocked_item:
            reason_text = f" Motivo: {blocked_item.reason}." if blocked_item.reason else ""
            messages.error(request, f'O item selecionado não pode ser retirado do servidor.{reason_text}')
            return redirect(f"{request.path}?char_id={char_id}")
        # -----------------------------------

        if not items:
            messages.error(request, 'Inventário não carregado.')
            return redirect('inventory:retirar_item')

        item_status = TransferFromCharToWallet.check_ingame_coin(item_id, char_id)
        if item_status['total'] < quantity:
            messages.error(request, 'Quantidade insuficiente no jogo.')
            return redirect(f"{request.path}?char_id={char_id}")

        success = TransferFromCharToWallet.remove_ingame_coin(item_id, quantity, char_id)
        if not success:
            messages.error(request, 'Falha ao remover o item do jogo.')
            return redirect(f"{request.path}?char_id={char_id}")
        
        # Localiza ou cria o inventário online do personagem
        inventory, _ = Inventory.objects.get_or_create(
            user=request.user,
            account_name=request.user.username,
            character_name=personagem[0]['char_name'],
        )

        # Verifica se já existe esse item no inventário
        inventory_item, _ = InventoryItem.objects.get_or_create(
            inventory=inventory,
            item_id=item_id,
            enchant=item_status['enchant'],
            defaults={'item_name': itens_data.get(str(item_id), [f"(não identificado - {str(item_id)})"])[0], 'quantity': 0}
        )

        # Atualiza a quantidade
        inventory_item.quantity += quantity
        inventory_item.save()

        messages.success(request, 'Item transferido com sucesso!')
        return redirect(f"{request.path}?char_id={char_id}")

    return render(request, 'pages/retirar_item.html', {
        'personagens': personagens,
        'char_id': char_id,
        'items': items,
        'personagem': personagem[0] if personagem else None
    })


@login_required
def inserir_item_servidor(request, char_name, item_id):
    db = LineageDB()
    if not db.is_connected():
        messages.error(request, 'O banco do jogo está indisponível no momento. Tente novamente mais tarde.')
        return redirect('inventory:inventario_dashboard')

    try:
        personagem = TransferFromWalletToChar.find_char(request.user.username, char_name)
        if not personagem:
            messages.error(request, 'Personagem não encontrado ou não pertence à sua conta.')
            return redirect('inventory:inventario_dashboard')

    except Exception as e:
        messages.error(request, f'Erro ao buscar personagem: {str(e)}')
        return redirect('inventory:inventario_dashboard')

    try:
        inventory = Inventory.objects.get(
            user=request.user,
            account_name=request.user.username,
            character_name=personagem[0]['char_name']
        )
        item = InventoryItem.objects.get(inventory=inventory, item_id=item_id)
    except InventoryItem.DoesNotExist:
        messages.error(request, 'Item não encontrado no inventário online.')
        return redirect('inventory:inventario_dashboard')

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))
        senha = request.POST.get('senha')

        user = authenticate(username=request.user.username, password=senha)
        if not user:
            messages.error(request, 'Senha incorreta.')
            return redirect(request.path)

        if item.quantity < quantity:
            messages.error(request, 'Quantidade insuficiente no inventário.')
            return redirect(request.path)
        
        success = TransferFromWalletToChar.insert_coin(personagem[0]['char_name'], item_id, quantity, item.enchant)
        if not success:
            messages.error(request, 'Falha ao inserir o item no servidor.')
            return redirect(request.path)

        item.quantity -= quantity

        if item.quantity == 0:
            item.delete()
        else:
            item.save()

        messages.success(request, f'{quantity}x {item.item_name} inserido no servidor com sucesso!')
        return redirect('inventory:inventario_dashboard')

    return render(request, 'pages/inserir_item_direct.html', {
        'personagem': personagem[0],
        'item': item,
    })


@login_required
@transaction.atomic
def trocar_item_com_jogador(request):
    if request.method == 'POST':
        character_name_origem = request.POST.get('character_name_origem')
        character_name_destino = request.POST.get('character_name_destino')
        item_id = int(request.POST.get('item_id').replace(',', '').replace('.', ''))
        quantity = int(request.POST.get('quantity').replace(',', '').replace('.', ''))

        inventario_origem = get_object_or_404(Inventory, character_name=character_name_origem, user=request.user)
        inventario_destino = get_object_or_404(Inventory, character_name=character_name_destino)

        try:
            item_origem = InventoryItem.objects.get(inventory=inventario_origem, item_id=item_id)
            if item_origem.quantity < quantity:
                messages.error(request, 'Quantidade insuficiente para troca.')
                return redirect('inventory:trocar_item')

            item_origem.quantity -= quantity
            if item_origem.quantity == 0:
                item_origem.delete()
            else:
                item_origem.save()

            item_destino, created = InventoryItem.objects.get_or_create(
                inventory=inventario_destino,
                item_id=item_id,
                defaults={'item_name': item_origem.item_name, 'quantity': quantity}
            )
            if not created:
                item_destino.quantity += quantity
                item_destino.save()

            messages.success(request, 'Troca realizada com sucesso!')
            return redirect('inventory:inventario_dashboard')

        except InventoryItem.DoesNotExist:
            messages.error(request, 'Item não encontrado no inventário de origem.')
            return redirect('inventory:trocar_item')

        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
            return redirect('inventory:trocar_item')

    # --- GET (preenche o form com os dados da querystring) ---
    character_name_origem = request.GET.get('character_name_origem', '')
    item_id = int(request.GET.get('item_id').replace(',', '').replace('.', ''))

    item_name = ''
    max_quantity = 0

    if character_name_origem and item_id:
        try:
            inventario = Inventory.objects.get(character_name=character_name_origem, user=request.user)
            item = InventoryItem.objects.get(inventory=inventario, item_id=item_id)
            item_name = item.item_name
            max_quantity = item.quantity
        except (Inventory.DoesNotExist, InventoryItem.DoesNotExist):
            messages.error(request, 'Item ou inventário não encontrado.')

    context = {
        'character_name_origem': character_name_origem,
        'item_id': item_id,
        'item_name': item_name,
        'max_quantity': max_quantity
    }
    return render(request, 'pages/trocar_item.html', context)


@login_required
def inventario_dashboard(request):
    inventories = Inventory.objects.filter(user=request.user)
    inventory_data = []

    for inv in inventories:
        inv.is_online = False  # ou use TransferFromCharToWallet pra pegar status real
        inv_items = InventoryItem.objects.filter(inventory=inv)
        inventory_data.append({
            'inventory': inv,
            'items': inv_items
        })

    return render(request, 'pages/inventario_dashboard.html', {
        'inventory_data': inventory_data
    })


@login_required
def inventario_global(request):
    # Agrupar os itens de todos os inventários do usuário e somar as quantidades
    itens_globais = InventoryItem.objects.filter(inventory__user=request.user) \
        .values('item_id', 'item_name') \
        .annotate(total_quantity=Sum('quantity')) \
        .order_by('-total_quantity')

    return render(request, 'pages/inventario_global.html', {
        'itens_globais': itens_globais
    })
