from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
from .forms import ThemeForm
from django.contrib import messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import helpers


@admin.register(ChatGroup)
class ChatGroupAdmin(BaseModelAdmin):
    list_display = ('group_name', 'sender', 'message_excerpt', 'timestamp')
    search_fields = ('group_name', 'sender__username', 'message')
    list_filter = ('group_name', 'timestamp')
    readonly_fields = ('timestamp',)

    def message_excerpt(self, obj):
        return obj.message[:20]
    message_excerpt.short_description = 'Message Excerpt'


@admin.register(Theme)
class ThemeAdmin(BaseModelAdmin):
    form = ThemeForm
    list_display = ('nome', 'slug', 'version', 'ativo')
    readonly_fields = ('nome', 'slug', 'version', 'author', 'descricao')
    fields = ('nome', 'slug', 'upload', 'version', 'author', 'descricao', 'ativo')
    actions = ['delete_selected_themes']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        obj.delete()

    def delete_selected_themes(self, request, queryset):
        """
        Handle the action to delete selected themes.
        If confirmation is required, display a confirmation page.
        """
        if "post" in request.POST:  # Confirmação de exclusão
            count = queryset.count()
            for obj in queryset:
                obj.delete()
            self.message_user(request, f"{count} tema(s) deletado(s) com sucesso.", messages.SUCCESS)
            return None  # Retorna None para seguir o fluxo padrão do Django Admin

        # Renderiza a tela de confirmação
        context = {
            'themes': queryset,
            'action_checkbox_name': helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, "admin/themes/delete_confirmation.html", context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    delete_selected_themes.short_description = "Excluir temas selecionados"
