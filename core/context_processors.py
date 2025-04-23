from django.conf import settings
from apps.main.administrator.models import Theme


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
    if theme:
        base_template = f"installed/{theme.slug}/base.html"
    else:
        base_template = "layouts/base-default.html"
    
    return {
        'active_theme': theme.slug if theme else None,
        'base_template': base_template,
    }
