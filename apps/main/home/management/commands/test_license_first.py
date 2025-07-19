from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
from utils.license_manager import check_license_status
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Testa se o LicenseBackend está sendo executado primeiro'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username para testar',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha para testar',
        )
        parser.add_argument(
            '--simulate-invalid',
            action='store_true',
            help='Simula licença inválida para teste',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔐 Teste do LicenseBackend como Primeiro Backend\n')
        )

        # 1. Mostra ordem dos backends
        self.stdout.write('📋 Ordem dos Backends Configurados:')
        for i, backend in enumerate(settings.AUTHENTICATION_BACKENDS, 1):
            marker = "🥇 PRIMEIRO" if i == 1 else f"#{i}"
            self.stdout.write(f'   {marker}: {backend}')

        # 2. Verifica status da licença
        self.stdout.write('\n📋 Status da Licença:')
        try:
            license_valid = check_license_status()
            self.stdout.write(f'   Status: {"✅ Válida" if license_valid else "❌ Inválida"}')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro ao verificar licença: {e}')
            return

        # 3. Simula licença inválida se solicitado
        if options['simulate_invalid']:
            self.stdout.write('\n🧪 SIMULANDO LICENÇA INVÁLIDA para teste...')
            # Temporariamente modifica a função para retornar False
            import utils.license_manager
            original_function = utils.license_manager.check_license_status
            
            def mock_invalid_license():
                return False
            
            utils.license_manager.check_license_status = mock_invalid_license

        # 4. Testa autenticação
        username = options['username']
        password = options['password']

        if not username or not password:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Use --username e --password para testar autenticação')
            )
            if options['simulate_invalid']:
                utils.license_manager.check_license_status = original_function
            return

        self.stdout.write(f'\n🧪 Testando autenticação para usuário: {username}')

        try:
            # Testa autenticação com Django authenticate
            user = authenticate(username=username, password=password)
            
            if user:
                self.stdout.write(f'   ✅ Login bem-sucedido')
                self.stdout.write(f'   📊 Backend usado: {user.backend}')
                
                # Verifica se o LicenseBackend foi usado
                if user.backend == 'core.backends.LicenseBackend':
                    self.stdout.write(f'   🎯 LicenseBackend foi usado (CORRETO!)')
                else:
                    self.stdout.write(f'   ⚠️ LicenseBackend não foi usado: {user.backend}')
                    
            else:
                if options['simulate_invalid']:
                    self.stdout.write(f'   ✅ Login bloqueado (licença inválida simulada - CORRETO!)')
                else:
                    self.stdout.write(f'   ❌ Login falhou (verifique credenciais)')
                    
        except Exception as e:
            self.stdout.write(f'   ❌ Erro na autenticação: {e}')

        # 5. Restaura função original se necessário
        if options['simulate_invalid']:
            utils.license_manager.check_license_status = original_function
            self.stdout.write('\n🔄 Função de licença restaurada')

        # 6. Testa LicenseBackend diretamente
        self.stdout.write(f'\n🔍 Testando LicenseBackend diretamente:')
        try:
            from core.backends import LicenseBackend
            backend = LicenseBackend()
            
            # Restaura função original se estava simulando
            if options['simulate_invalid']:
                utils.license_manager.check_license_status = mock_invalid_license
            
            user = backend.authenticate(None, username=username, password=password)
            
            if user:
                self.stdout.write(f'   ✅ LicenseBackend permitiu login')
            else:
                if options['simulate_invalid']:
                    self.stdout.write(f'   ✅ LicenseBackend bloqueou login (licença inválida)')
                else:
                    self.stdout.write(f'   ❌ LicenseBackend falhou na autenticação')
                    
        except Exception as e:
            self.stdout.write(f'   ❌ Erro no LicenseBackend: {e}')

        # 7. Restaura função original
        if options['simulate_invalid']:
            utils.license_manager.check_license_status = original_function

        # 8. Recomendações
        self.stdout.write(f'\n💡 Recomendações:')
        self.stdout.write(f'   • LicenseBackend deve ser o PRIMEIRO backend na lista')
        self.stdout.write(f'   • Todos os logins devem passar pelo LicenseBackend primeiro')
        self.stdout.write(f'   • Use --simulate-invalid para testar bloqueio de licença')
        self.stdout.write(f'   • Monitore os logs para verificar a execução') 