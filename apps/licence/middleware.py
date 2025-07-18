from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from .manager import license_manager


class LicenseMiddleware:
    """
    Middleware para verificar licença em tempo real
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Lista de URLs que não precisam de verificação de licença
        exempt_urls = [
            '/admin/',
            '/static/',
            '/media/',
            '/accounts/',
            '/public/',
            '/api/license/',
            '/license/',
            '/activate/',
            '/health/',
        ]
        
        # Verifica se a URL atual está na lista de exceções
        path = request.path_info
        is_exempt = any(path.startswith(url) for url in exempt_urls)
        
        # Adiciona informações de licença ao request
        request.license_status = {
            'is_valid': False,
            'has_license': False,
            'license_info': None,
            'show_warning': False
        }
        
        # Se não for exceção, verifica a licença
        if not is_exempt:
            # Verifica se há licença ativa
            current_license = license_manager.get_current_license()
            if current_license:
                request.license_status['has_license'] = True
                request.license_status['license_info'] = license_manager.get_license_info()
                
                # Verifica se a licença está válida
                is_valid = license_manager.check_license_status(request)
                request.license_status['is_valid'] = is_valid
                
                # Mostra aviso se não for superusuário ou se a licença for inválida
                if not is_valid or (hasattr(request, 'user') and request.user.is_authenticated and not request.user.is_superuser):
                    request.license_status['show_warning'] = True
            else:
                # Não há licença ativa
                request.license_status['show_warning'] = True
        
        response = self.get_response(request)
        return response


class LicenseFeatureMiddleware:
    """
    Middleware para verificar funcionalidades específicas da licença
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Adiciona informações da licença ao request
        request.license_info = license_manager.get_license_info()
        request.can_use_feature = lambda feature: license_manager.can_use_feature(feature, request)
        
        response = self.get_response(request)
        return response 