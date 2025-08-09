from django.core.management.base import BaseCommand
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.licence.middleware import LicenseMiddleware
from apps.main.licence.manager import license_manager

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o middleware de licença'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Testando middleware de licença...'))
        
        # Cria um request factory
        factory = RequestFactory()
        
        # Cria um request simulado
        request = factory.get('/dashboard/')
        
        # Simula um usuário autenticado
        user = User.objects.filter(is_superuser=True).first()
        if user:
            request.user = user
        else:
            self.stdout.write(self.style.WARNING('Nenhum superusuário encontrado'))
            return
        
        # Aplica o middleware
        middleware = LicenseMiddleware(lambda req: None)
        middleware(request)
        
        # Verifica o status da licença
        self.stdout.write(f'Status da licença no request: {request.license_status}')
        
        # Verifica se há licença ativa
        current_license = license_manager.get_current_license()
        if current_license:
            self.stdout.write(self.style.SUCCESS(f'Licença ativa encontrada: {current_license.license_key}'))
            self.stdout.write(f'Tipo: {current_license.license_type}')
            self.stdout.write(f'Status: {current_license.status}')
            self.stdout.write(f'Expira em: {current_license.expires_at}')
        else:
            self.stdout.write(self.style.WARNING('Nenhuma licença ativa encontrada'))
        
        # Verifica se o aviso deve ser mostrado
        if request.license_status.get('show_warning'):
            self.stdout.write(self.style.WARNING('⚠️ Aviso de licença deve ser mostrado no dashboard'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Licença válida - nenhum aviso necessário')) 