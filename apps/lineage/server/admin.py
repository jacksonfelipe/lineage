from django.contrib import admin
from .models import ApiEndpointToggle, IndexConfig, IndexConfigTranslation, ServicePrice
from core.admin import BaseModelAdmin
from django.contrib import messages


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


class IndexConfigTranslationInline(admin.TabularInline):
    model = IndexConfigTranslation
    extra = 1
    fields = ('language', 'nome_servidor', 'descricao_servidor', 'jogadores_online_texto')
    min_num = 1


@admin.register(IndexConfig)
class IndexConfigAdmin(BaseModelAdmin):
    list_display = (
        'nome_servidor', 'link_patch', 'link_cliente', 'link_discord', 
        'trailer_video_id', 'imagem_banner'
    )
    search_fields = ('nome_servidor',)
    list_filter = ()

    inlines = [IndexConfigTranslationInline]

    fieldsets = (
        (None, {
            'fields': ('nome_servidor', 'descricao_servidor', 'link_patch', 'link_cliente', 'link_discord')
        }),
        ('Configurações de Trailer', {
            'fields': ('trailer_video_id',)
        }),
        ('Configurações de Exibição', {
            'fields': ('jogadores_online_texto', 'imagem_banner')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change and IndexConfig.objects.exists():
            self.message_user(
                request,
                "Apenas um registro de configuração do servidor pode existir. Por favor, edite o existente.",
                messages.WARNING
            )
            return
        super().save_model(request, obj, form, change)


@admin.register(ServicePrice)
class ServicePriceAdmin(BaseModelAdmin):
    list_display = ('servico', 'preco')
