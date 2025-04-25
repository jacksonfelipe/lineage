from django.conf import settings
from apps.main.administrator.models import Theme
import os
from django.utils.text import slugify


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
    base_template = "layouts/base-default.html"
    theme_files = {}

    if theme:
        safe_slug = slugify(theme.slug)
        theme_path = os.path.join(settings.BASE_DIR, 'themes', 'installed', safe_slug)

        if os.path.isdir(theme_path):
            theme_files = {
                f: os.path.join('installed', safe_slug, f)
                for f in os.listdir(theme_path)
                if os.path.isfile(os.path.join(theme_path, f))
            }

        base_template = f"installed/{safe_slug}/base.html"
    
    return {
        'active_theme': safe_slug if theme else None,
        'base_template': base_template,
        'theme_slug': safe_slug if theme else None,
        'path_theme': f'themes/installed/{safe_slug}' if theme else None,
        'theme_files': theme_files,
    }
