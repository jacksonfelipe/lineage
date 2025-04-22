from django.contrib import admin
from .models import *
from core.admin import BaseModelAdmin
import zipfile, os, json


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
class ThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'version', 'active')
    readonly_fields = ('name', 'slug', 'version', 'author', 'description')

    def save_model(self, request, obj, form, change):
        if obj.upload:
            # Cria pasta themes se não existir
            os.makedirs('themes', exist_ok=True)

            # Extrai o zip
            zip_path = obj.upload.path
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall('themes')

            # Lê o theme.json
            extracted_folder = zipfile.ZipFile(zip_path).namelist()[0].split('/')[0]
            theme_json_path = os.path.join('themes', extracted_folder, 'theme.json')

            with open(theme_json_path) as f:
                meta = json.load(f)

            # Atualiza os dados
            obj.name = meta['name']
            obj.slug = meta['slug']
            obj.version = meta['version']
            obj.author = meta['author']
            obj.description = meta['description']

            # Remove o arquivo enviado
            os.remove(zip_path)
            obj.upload = None

        super().save_model(request, obj, form, change)
