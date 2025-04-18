from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ShopItem, ShopPackage, Cart, CartItem, CartPackage, PromotionCode, ShopPurchase
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.inventory.models import InventoryItem, Inventory
from django.contrib.admin.views.decorators import staff_member_required
from .forms import ShopItemForm, ShopPackageForm, PromotionCodeForm


@login_required
def shop_home(request):
    items = ShopItem.objects.filter(ativo=True)
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
    cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
    if not created:
        cart_item.quantidade += 1
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
    if not personagem:
        messages.error(request, "Informe o nome do personagem para entrega.")
        return redirect('shop:view_cart')

    # Descontar do saldo
    aplicar_transacao(wallet, 'SAIDA', total, descricao="Compra no Shop")

    # Enviar itens e pacotes para o inventário
    inventory, _ = Inventory.objects.get_or_create(user=request.user, account_name=request.user.username, character_name=personagem)

    # Adicionar os itens do carrinho no inventário
    for cart_item in cart.cartitem_set.all():
        quantidade_total = cart_item.quantidade * cart_item.item.quantidade

        existing_item = InventoryItem.objects.filter(inventory=inventory, item_id=cart_item.item.item_id).first()

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

            existing_item = InventoryItem.objects.filter(inventory=inventory, item_id=pacote_item.item.item_id).first()

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


@login_required
def purchase_history(request):
    purchases = ShopPurchase.objects.filter(user=request.user).order_by('-data_compra')
    return render(request, 'shop/purchases.html', {'purchases': purchases})


@staff_member_required
def admin_items(request):
    items = ShopItem.objects.all()
    if request.method == 'POST':
        form = ShopItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_items')
    else:
        form = ShopItemForm()

    return render(request, 'shop/admin_items.html', {'form': form, 'items': items})


@staff_member_required
def admin_packages(request):
    packages = ShopPackage.objects.all()
    if request.method == 'POST':
        form = ShopPackageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_packages')
    else:
        form = ShopPackageForm()

    return render(request, 'shop/admin_packages.html', {'form': form, 'packages': packages})


@staff_member_required
def admin_promotions(request):
    promotions = PromotionCode.objects.all()
    if request.method == 'POST':
        form = PromotionCodeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('shop:admin_promotions')
    else:
        form = PromotionCodeForm()

    return render(request, 'shop/admin_promotions.html', {'form': form, 'promotions': promotions})


@staff_member_required
def admin_dashboard(request):
    return render(request, 'shop/admin_dashboard.html')
