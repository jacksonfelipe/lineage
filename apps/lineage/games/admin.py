from django.contrib import admin
from .models import Prize, SpinHistory
from core.admin import BaseModelAdmin
from django.utils.html import format_html


@admin.register(Prize)
class PrizeAdmin(BaseModelAdmin):
    list_display = ('name', 'image_preview', 'weight', 'created_at', 'updated_at')
    search_fields = ('name',)
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

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
