from django.contrib import admin
from core.admin import BaseModelAdmin
from .models import *


# Só deixar ativo o que for realmente útil de emergência ou manutenção
@admin.register(ShopItem)
class ShopItemAdmin(BaseModelAdmin):
    list_display = ('nome', 'item_id', 'quantidade', 'preco', 'ativo')
    list_filter = ('ativo',)
    search_fields = ('nome', 'item_id')
    ordering = ('nome',)


@admin.register(ShopPackage)
class ShopPackageAdmin(BaseModelAdmin):
    list_display = ('nome', 'preco_total', 'ativo', 'promocao')
    list_filter = ('ativo', 'promocao')
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(PromotionCode)
class PromotionCodeAdmin(BaseModelAdmin):
    list_display = ('codigo', 'desconto_percentual', 'ativo', 'validade')
    search_fields = ('codigo',)
    ordering = ('-validade',)


# Opcional — se quiser manter acesso rápido ao carrinho
@admin.register(Cart)
class CartAdmin(BaseModelAdmin):
    list_display = ('user', 'promocao_aplicada', 'calcular_total')
    search_fields = ('user__username',)
    ordering = ('user',)


@admin.register(ShopPurchase)
class ShopPurchaseAdmin(BaseModelAdmin):
    list_display = ('user', 'character_name', 'total_pago', 'data_compra', 'promocao_aplicada')
    list_filter = ('data_compra',)
    search_fields = ('user__username', 'character_name')
    ordering = ('-data_compra',)
