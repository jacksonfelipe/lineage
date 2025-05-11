from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
from django.utils.html import format_html
from .forms import BoxTypeAdminForm


@admin.register(Prize)
class PrizeAdmin(BaseModelAdmin):
    list_display = ('name', 'image_preview', 'weight', 'item_id', 'enchant', 'rarity', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at', 'rarity')
    readonly_fields = ('created_at', 'updated_at')
    
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


@admin.register(Item)
class ItemAdmin(BaseModelAdmin):
    list_display = ('name', 'item_id', 'enchant', 'rarity', 'can_be_populated', 'description')
    list_editable = ('can_be_populated',)
    search_fields = ('name', 'item_id')
    list_filter = ('rarity', 'enchant', 'can_be_populated')
    ordering = ('name',)


@admin.register(BoxType)
class BoxTypeAdmin(BaseModelAdmin):
    form = BoxTypeAdminForm
    
    list_display = (
        'name', 'price', 'boosters_amount',
        'chance_common', 'chance_rare', 'chance_epic', 'chance_legendary',
        'max_epic_items', 'max_legendary_items'
    )
    search_fields = ('name',)
    list_filter = ('price', 'boosters_amount')
    ordering = ('name',)
    filter_horizontal = ('allowed_items',)

    fieldsets = (
        (None, {
            'fields': (
                'name', 'price', 'boosters_amount',
                'allowed_items'
            )
        }),
        ('Chances de Raridade (%)', {
            'fields': (
                'chance_common', 'chance_rare',
                'chance_epic', 'chance_legendary'
            )
        }),
        ('Limites por Raridade', {
            'fields': (
                'max_epic_items', 'max_legendary_items',
            )
        }),
    )


@admin.register(Box)
class BoxAdmin(BaseModelAdmin):
    list_display = ('user', 'box_type', 'opened', 'created_at')
    search_fields = ('user__username', 'box_type__name')
    list_filter = ('opened', 'created_at')
    ordering = ('-created_at',)


@admin.register(BoxItem)
class BoxItemAdmin(BaseModelAdmin):
    list_display = ('box', 'item', 'opened', 'probability')
    search_fields = ('box__user__username', 'item__name')
    list_filter = ('opened',)
    ordering = ('box', 'item')


@admin.register(BoxItemHistory)
class BoxItemHistoryAdmin(BaseModelAdmin):
    list_display = ('user', 'item', 'enchant', 'rarity', 'box', 'obtained_at')
    list_filter = ('rarity', 'obtained_at')
    search_fields = ('user__username', 'item__name')
    ordering = ('-obtained_at',)
    readonly_fields = ('user', 'item', 'box', 'rarity', 'enchant', 'obtained_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Recompensa)
class RecompensaAdmin(BaseModelAdmin):
    list_display = ('tipo', 'referencia', 'item_name', 'quantity', 'enchant')
    list_filter = ('tipo',)
    search_fields = ('referencia', 'item_name')


@admin.register(RecompensaRecebida)
class RecompensaRecebidaAdmin(admin.ModelAdmin):
    list_display = ('user', 'recompensa', 'data')
    list_filter = ('data',)
    search_fields = ('user__username', 'recompensa__item_name', 'recompensa__tipo')
    ordering = ('-data',)
