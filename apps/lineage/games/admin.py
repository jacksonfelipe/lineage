from django.contrib import admin
from .models import Prize, SpinHistory, BagItem, Bag
from core.admin import BaseModelAdmin
from django.utils.html import format_html


@admin.register(Prize)
class PrizeAdmin(BaseModelAdmin):
    # Exibição da lista de prêmios
    list_display = ('name', 'image_preview', 'weight', 'item_id', 'enchant', 'rarity', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'rarity')  # Filtra por raridade e data
    readonly_fields = ('created_at', 'updated_at')
    
    # Campos que podem ser editados no form de detalhes
    fieldsets = (
        (None, {
            'fields': ('name', 'item_id', 'image', 'weight', 'enchant', 'rarity')
        }),
        ('Datas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        return format_html(
            '<img src="{}" width="50" height="50" style="object-fit: contain; border: 1px solid #ccc; border-radius: 6px;" />',
            obj.get_image_url()
        )
    image_preview.short_description = 'Imagem'


@admin.register(SpinHistory)
class SpinHistoryAdmin(BaseModelAdmin):
    list_display = ('user', 'prize', 'created_at')
    search_fields = ('user__username', 'prize__name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Bag)
class BagAdmin(BaseModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(BagItem)
class BagItemAdmin(BaseModelAdmin):
    list_display = ('bag', 'item_name', 'enchant', 'quantity', 'added_at')
    search_fields = ('item_name', 'bag__user__username')
    list_filter = ('enchant', 'added_at')
    readonly_fields = ('added_at',)
    ordering = ('-added_at',)
