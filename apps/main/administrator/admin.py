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
            try:
                # Cria a pasta base de temas, se necessário
                os.makedirs('themes', exist_ok=True)

                # Extrai o zip
                zip_path = obj.upload.path
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    extracted_folder = zip_ref.namelist()[0].split('/')[0]
                    theme_path = os.path.join('themes', extracted_folder)
                    zip_ref.extractall('themes')

                # Lê o theme.json
                theme_json_path = os.path.join(theme_path, 'theme.json')
                if not os.path.exists(theme_json_path):
                    raise ValidationError("O arquivo theme.json não foi encontrado no tema.")

                with open(theme_json_path, encoding='utf-8') as f:
                    meta = json.load(f)

                # Verifica se o base.html existe no tema
                expected_template = os.path.join(theme_path, 'base.html')
                if not os.path.exists(expected_template):
                    raise ValidationError("O arquivo base.html não foi encontrado no tema.")

                # Define os dados do tema com base no JSON
                slug = meta.get('slug')
                if not slug:
                    raise ValidationError("O campo 'slug' é obrigatório no theme.json.")

                new_path = os.path.join('themes', slug)

                # Renomeia pasta, se o slug for diferente
                if extracted_folder != slug:
                    if os.path.exists(new_path):
                        raise ValidationError(f"Já existe um tema com o slug '{slug}'.")
                    os.rename(theme_path, new_path)
                else:
                    new_path = theme_path  # pasta já está correta

                obj.nome = meta.get('name', obj.nome)
                obj.slug = slug
                obj.version = meta.get('version', '')
                obj.author = meta.get('author', '')
                obj.descricao = meta.get('description', '')

                # Remove o zip original
                os.remove(zip_path)
                obj.upload = None

            except (ValidationError, zipfile.BadZipFile, json.JSONDecodeError, KeyError) as e:
                messages.error(request, f"Erro ao instalar o tema: {str(e)}")
                return

        super().save_model(request, obj, form, change)
