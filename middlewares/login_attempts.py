import time
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class LoginAttemptsMiddleware:
    """
    Middleware para rastrear tentativas de login e gerenciar captcha
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Processa a requisição
        response = self.get_response(request)
        
        # Verifica se é uma tentativa de login
        if request.method == 'POST' and request.path.endswith('/login/'):
            self._handle_login_attempt(request, response)
        
        return response
    
    def _handle_login_attempt(self, request, response):
        """Gerencia tentativas de login"""
        # Só incrementa tentativas se a resposta não for um redirecionamento bem-sucedido
        # O reset das tentativas será feito na view quando o login for bem-sucedido
        if response.status_code != 302:
            client_ip = self._get_client_ip(request)
            cache_key = f"login_attempts_{client_ip}"
            
            # Obtém tentativas atuais e incrementa
            attempts = cache.get(cache_key, 0) + 1
            cache.set(cache_key, attempts, 3600)  # Expira em 1 hora
            logger.warning(f"Tentativa de login falhou para IP {client_ip}, tentativa {attempts}")
    
    def _get_client_ip(self, request):
        """Obtém o IP real do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def get_login_attempts(request):
        """Retorna o número de tentativas de login para o IP"""
        client_ip = LoginAttemptsMiddleware._get_client_ip_static(request)
        cache_key = f"login_attempts_{client_ip}"
        return cache.get(cache_key, 0)
    
    @staticmethod
    def _get_client_ip_static(request):
        """Versão estática para obter IP do cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @staticmethod
    def requires_captcha(request):
        """Verifica se o captcha é necessário"""
        attempts = LoginAttemptsMiddleware.get_login_attempts(request)
        return attempts >= getattr(settings, 'LOGIN_MAX_ATTEMPTS', 3)
    
    @staticmethod
    def reset_attempts(request):
        """Reseta as tentativas de login"""
        client_ip = LoginAttemptsMiddleware._get_client_ip_static(request)
        cache_key = f"login_attempts_{client_ip}"
        cache.delete(cache_key)
        logger.info(f"Tentativas de login resetadas para IP {client_ip}") 