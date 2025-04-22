from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
import zipfile, os, json
from django.contrib import messages


# Register your models here.
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
    list_display = ('nome', 'slug', 'version', 'ativo')
    readonly_fields = ('nome', 'slug', 'version', 'author', 'descricao')
    
    def save_model(self, request, obj, form, change):
        if obj.upload:
            # Verifique o diretório media
            upload_path = obj.upload.path  # O Django deve gerenciar este caminho
            media_dir = os.path.dirname(upload_path)

            # Cria a pasta se não existir
            os.makedirs('themes', exist_ok=True)

            # Extrai o arquivo ZIP
            with zipfile.ZipFile(upload_path, 'r') as zip_ref:
                zip_ref.extractall('themes')

            # Processa o tema extraído
            extracted_folder = zipfile.ZipFile(upload_path).namelist()[0].split('/')[0]
            theme_json_path = os.path.join('themes', extracted_folder, 'theme.json')

            # Lê o theme.json
            with open(theme_json_path) as f:
                meta = json.load(f)

            # Atualiza os dados do tema com informações do JSON
            obj.nome = meta.get('name', obj.nome)
            obj.slug = meta.get('slug', obj.slug)
            obj.version = meta.get('version', '')
            obj.author = meta.get('author', '')
            obj.descricao = meta.get('description', '')

            # Remove o arquivo ZIP após processar
            os.remove(upload_path)
            obj.upload = None  # Limpa o campo de upload

        super().save_model(request, obj, form, change)
