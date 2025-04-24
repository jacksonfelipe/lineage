from django.conf import settings
from apps.main.administrator.models import Theme
import os


def project_metadata(request):
    return {
        'PROJECT_TITLE': settings.PROJECT_TITLE,
        'PROJECT_AUTHOR': settings.PROJECT_AUTHOR,
        'PROJECT_DESCRIPTION': settings.PROJECT_DESCRIPTION,
        'PROJECT_KEYWORDS': settings.PROJECT_KEYWORDS,
        'PROJECT_URL': settings.PROJECT_URL,
        'PROJECT_LOGO_URL': settings.PROJECT_LOGO_URL,
        'PROJECT_FAVICON_ICO': settings.PROJECT_FAVICON_ICO,
        'PROJECT_FAVICON_MANIFEST': settings.PROJECT_FAVICON_MANIFEST,
        'PROJECT_THEME_COLOR': settings.PROJECT_THEME_COLOR,
        'PROJECT_DISCORD_URL': settings.PROJECT_DISCORD_URL,
        'PROJECT_YOUTUBE_URL': settings.PROJECT_YOUTUBE_URL,
        'PROJECT_FACEBOOK_URL': settings.PROJECT_FACEBOOK_URL,
        'PROJECT_INSTAGRAM_URL': settings.PROJECT_INSTAGRAM_URL,
    }


def active_theme(request):
    theme = Theme.objects.filter(ativo=True).first()
    base_template = "layouts/base-default.html"  # Template base padrão
    
    # Lista de arquivos do tema ativo
    theme_files = {}

    if theme:
        # Caminho para o diretório do tema ativo
        theme_path = os.path.join(settings.BASE_DIR, 'templates', 'installed', theme.slug)

        # Verificar se o diretório do tema existe
        if os.path.isdir(theme_path):
            # Listar todos os arquivos dentro do diretório do tema
            theme_files = {f: os.path.join('installed', theme.slug, f) for f in os.listdir(theme_path) if os.path.isfile(os.path.join(theme_path, f))}

        # Definir o template base do tema
        base_template = f"installed/{theme.slug}/base.html"  # O base é sempre o mesmo para o tema
    
    return {
        'active_theme': theme.slug if theme else None,
        'base_template': base_template,
        'theme_slug': theme.slug if theme else None,
        'theme_files': theme_files,  # Lista de arquivos do tema
    }
