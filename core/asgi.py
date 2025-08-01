"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Tenta importar as rotas do administrator, mas trata o erro caso o app não exista
try:
    from apps.main.administrator.routing import websocket_urlpatterns as admin_ws
except ImportError:
    admin_ws = []
try:
    from apps.main.notification.routing import websocket_urlpatterns as notif_ws
except ImportError:
    notif_ws = []

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            admin_ws + notif_ws
        )
    ),
})
