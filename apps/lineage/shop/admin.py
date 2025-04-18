from django.contrib import admin
from core.admin import BaseModelAdmin
from .models import (
    ShopItem, ShopPackage, ShopPackageItem,
    PromotionCode, Cart, CartItem, CartPackage, ShopPurchase
)


@admin.register(ShopItem)
class ShopItemAdmin(BaseModelAdmin):
    list_display = ('nome', 'item_id', 'quantidade', 'preco', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'item_id')
    ordering = ('nome',)


class ShopPackageItemInline(admin.TabularInline):
    model = ShopPackageItem
    extra = 1


@admin.register(ShopPackage)
class ShopPackageAdmin(BaseModelAdmin):
    list_display = ('nome', 'preco_total', 'ativo', 'promocao')
    list_filter = ('ativo', 'promocao')
    search_fields = ('nome',)
    ordering = ('nome',)
    inlines = [ShopPackageItemInline]


@admin.register(PromotionCode)
class PromotionCodeAdmin(BaseModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'ativo', 'validade')
    list_filter = ('ativo',)
    search_fields = ('codigo',)
    ordering = ('-validade',)


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0


class CartPackageInline(admin.TabularInline):
    model = CartPackage
    extra = 0


@admin.register(Cart)
class CartAdmin(BaseModelAdmin):
    list_display = ('user', 'promocao_aplicada', 'calcular_total')
    search_fields = ('user__username',)
    inlines = [CartItemInline, CartPackageInline]


@admin.register(ShopPurchase)
class ShopPurchaseAdmin(BaseModelAdmin):
    list_display = ('user', 'character_name', 'total_pago', 'data_compra', 'promocao_aplicada')
    list_filter = ('data_compra',)
    search_fields = ('user__username', 'character_name')
    ordering = ('-data_compra',)
