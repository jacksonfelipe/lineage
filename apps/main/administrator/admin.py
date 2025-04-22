from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
from .forms import ThemeForm


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
class ThemeAdmin(admin.ModelAdmin):
    form = ThemeForm  # Usa o formulário personalizado
    list_display = ('nome', 'slug', 'version', 'ativo')  # Exibe as colunas na listagem do admin
    readonly_fields = ('nome', 'slug', 'version', 'author', 'descricao')  # Campos apenas para leitura
    fields = ('nome', 'slug', 'upload', 'version', 'author', 'descricao', 'ativo')  # Campos para edição
    
    def save_model(self, request, obj, form, change):
        # Não é necessário fazer o processamento aqui, pois isso é feito dentro do modelo
        super().save_model(request, obj, form, change)  # Apenas chama o save_model padrão do Django
