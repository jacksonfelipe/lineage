from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin


class InventoryItemInline(admin.TabularInline):
    model = InventoryItem
    extra = 1


@admin.register(Inventory)
class InventoryAdmin(BaseModelAdmin):
    list_display = ('character_name', 'account_name', 'user', 'created_at')
    search_fields = ('character_name', 'account_name', 'user__username')
    inlines = [InventoryItemInline]


@admin.register(InventoryItem)
class InventoryItemAdmin(BaseModelAdmin):
    list_display = ('item_name', 'inventory', 'quantity', 'added_at')
    list_filter = ('inventory',)
    search_fields = ('item_name', 'inventory__character_name')


@admin.register(BlockedServerItem)
class BlockedServerItemAdmin(BaseModelAdmin):
    list_display = ('item_id', 'reason', 'created_at')
    search_fields = ('item_id', 'reason')
