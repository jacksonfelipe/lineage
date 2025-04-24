from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import ShopItem, ShopPackage, Cart, CartItem, CartPackage, PromotionCode, ShopPurchase
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory


@login_required
def shop_home(request):
    items = ShopItem.objects.filter(ativo=True)
    print(items)
    packages = ShopPackage.objects.filter(ativo=True)
    return render(request, 'shop/home.html', {
        'items': items,
        'packages': packages
    })


@login_required
def view_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'shop/cart.html', {'cart': cart})


@login_required
def add_item_to_cart(request, item_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    item = get_object_or_404(ShopItem, id=item_id, ativo=True)
    
    quantidade = int(request.POST.get('quantidade', 1))
    if quantidade < 1:
        messages.error(request, "A quantidade deve ser maior que zero.")
        return redirect('shop:shop_home')
        
    if quantidade > 99:  # Limite máximo por item
        messages.error(request, "Quantidade máxima excedida.")
        return redirect('shop:shop_home')
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantidade += quantidade
        if cart_item.quantidade > 99:
            messages.error(request, "Quantidade máxima no carrinho excedida.")
            return redirect('shop:shop_home')
    else:
        cart_item.quantidade = quantidade
    cart_item.save()
    
    messages.success(request, f"{item.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@login_required
def add_package_to_cart(request, package_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    pacote = get_object_or_404(ShopPackage, id=package_id, ativo=True)
    cart_package, created = CartPackage.objects.get_or_create(cart=cart, pacote=pacote)
    if not created:
        cart_package.quantidade += 1
    cart_package.save()
    messages.success(request, f"Pacote {pacote.nome} adicionado ao carrinho.")
    return redirect('shop:shop_home')


@login_required
def apply_promo_code(request):
    if request.method == "POST":
        code = request.POST.get("promo_code")
        cart, _ = Cart.objects.get_or_create(user=request.user)
        try:
            promo = PromotionCode.objects.get(codigo=code, ativo=True)
            if not promo.is_valido():
                messages.error(request, "Código expirado ou inválido.")
            else:
                cart.promocao_aplicada = promo
                cart.save()
                messages.success(request, f"Cupom {promo.codigo} aplicado!")
        except PromotionCode.DoesNotExist:
            messages.error(request, "Cupom não encontrado.")
    return redirect('shop:view_cart')


@login_required
def checkout(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    wallet = request.user.wallet

    total = cart.calcular_total()

    if wallet.saldo < total:
        messages.error(request, "Saldo insuficiente na carteira.")
        return redirect('shop:view_cart')

    personagem = request.POST.get('character_name')
    if not personagem or len(personagem.strip()) < 3:
        messages.error(request, "Informe um nome de personagem válido para entrega (mínimo 3 caracteres).")
        return redirect('shop:view_cart')

    if not cart.cartitem_set.exists() and not cart.cartpackage_set.exists():
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('shop:view_cart')

    try:
        with transaction.atomic():
            # Descontar do saldo
            aplicar_transacao(wallet, 'SAIDA', total, descricao="Compra no Shop")

            # Enviar itens e pacotes para o inventário
            inventory, _ = Inventory.objects.get_or_create(
                user=request.user,
                account_name=request.user.username,
                character_name=personagem
            )

            # Adicionar os itens do carrinho no inventário
            for cart_item in cart.cartitem_set.all():
                quantidade_total = cart_item.quantidade * cart_item.item.quantidade

                existing_item = InventoryItem.objects.filter(
                    inventory=inventory,
                    item_id=cart_item.item.item_id
                ).first()

                if existing_item:
                    existing_item.quantity += quantidade_total
                    existing_item.save()
                else:
                    InventoryItem.objects.create(
                        inventory=inventory,
                        item_id=cart_item.item.item_id,
                        item_name=cart_item.item.nome,
                        quantity=quantidade_total
                    )

            # Adicionar os itens dos pacotes no inventário
            for cart_package in cart.cartpackage_set.all():
                for pacote_item in cart_package.pacote.shoppackageitem_set.all():
                    quantidade_total = pacote_item.quantidade * pacote_item.item.quantidade * cart_package.quantidade

                    existing_item = InventoryItem.objects.filter(
                        inventory=inventory,
                        item_id=pacote_item.item.item_id
                    ).first()

                    if existing_item:
                        existing_item.quantity += quantidade_total
                        existing_item.save()
                    else:
                        InventoryItem.objects.create(
                            inventory=inventory,
                            item_id=pacote_item.item.item_id,
                            item_name=pacote_item.item.nome,
                            quantity=quantidade_total
                        )

            # Registrar a compra
            ShopPurchase.objects.create(
                user=request.user,
                character_name=personagem,
                total_pago=total,
                promocao_aplicada=cart.promocao_aplicada
            )

            cart.limpar()
            messages.success(request, "Compra realizada com sucesso! Itens enviados para o inventário.")
            return redirect('shop:purchase_history')

    except Exception as e:
        messages.error(request, "Erro ao processar a compra. Por favor, tente novamente.")
        return redirect('shop:view_cart')


@login_required
def purchase_history(request):
    purchases = ShopPurchase.objects.filter(user=request.user).order_by('-data_compra')
    return render(request, 'shop/purchases.html', {'purchases': purchases})


@login_required
def clear_cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart.limpar()
    messages.success(request, "Carrinho esvaziado com sucesso.")
    return redirect('shop:view_cart')
