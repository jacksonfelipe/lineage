from django.contrib.auth.backends import ModelBackend
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from utils.license_manager import check_license_status

class LicenseBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = super().authenticate(request, username, password, **kwargs)

        if user and user.is_superuser:
            if not check_license_status():
                if request:
                    messages.error(request, "Erro: A licença do sistema não é válida. Contate o administrador.")
                    # Você pode querer redirecionar o usuário ou simplesmente não retornar o usuário
                    # e deixar que o fluxo de login padrão do Django lide com isso.
                    # return None # Impediria o login do superusuário
                    
                    # Alternativamente, para um erro mais explícito e um redirecionamento personalizado:
                    # return None # Garante que o usuário não será logado pelo backend

                print("[LicenseBackend] Tentativa de login de superusuário com licença inválida.")
                return None  # Impede o login do superusuário

        return user

    def get_user(self, user_id):
        try:
            return super().get_user(user_id)
        except Exception:
            return None 