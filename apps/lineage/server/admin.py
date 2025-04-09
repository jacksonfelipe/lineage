from django.contrib import admin
from .models import ApiEndpointToggle
from core.admin import BaseModelAdmin


@admin.register(ApiEndpointToggle)
class ApiEndpointToggleAdmin(BaseModelAdmin):
    list_display = [
        'players_online',
        'top_pvp',
        'top_pk',
        'top_clan',
        'top_rich',
        'top_online',
        'top_level',
        'olympiad_ranking',
        'olympiad_all_heroes',
        'olympiad_current_heroes',
        'grandboss_status',
        'raidboss_status',
        'siege',
        'siege_participants',
        'boss_jewel_locations',
    ]

    list_editable = list_display  # permite edição inline no list view
    list_display_links = None  # remove link para a edição detalhada
    actions = None  # remove ações em massa para evitar exclusões acidentais

    def has_add_permission(self, request):
        # Permite adicionar apenas se ainda não houver nenhum registro
        return not ApiEndpointToggle.objects.exists()

    def has_delete_permission(self, request, obj=None):
        # Impede a exclusão do registro
        return False
