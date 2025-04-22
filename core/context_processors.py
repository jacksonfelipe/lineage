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
    }


def active_theme(request):
    theme = Theme.objects.filter(ativo=True).first()
    return {
        'active_theme': theme.slug if theme else None
    }
