from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse


class SessionLockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Libera acesso a arquivos estáticos, de mídia e arquivos descriptografados
        if (
            path.startswith(settings.STATIC_URL)
            or path.startswith(settings.MEDIA_URL)
            or path.startswith('/decrypted-file/')
        ):
            return self.get_response(request)

        # Verifica se o usuário está bloqueado
        locked = request.session.get('is_locked', False)
        is_locked_path = path == reverse('lock')

        if request.user.is_authenticated and locked and not is_locked_path:
            return redirect('lock')

        return self.get_response(request)
