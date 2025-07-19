from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
from utils.license_manager import check_license_status
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Testa especificamente o LicenseBackend com superusuários'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username do superusuário para testar',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do superusuário',
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Apenas verifica o status da licença',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔐 Teste do LicenseBackend\n')
        )

        # 1. Verifica status da licença
        self.stdout.write('📋 Verificando status da licença:')
        try:
            license_valid = check_license_status()
            self.stdout.write(f'   Status: {"✅ Válida" if license_valid else "❌ Inválida"}')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro ao verificar licença: {e}')
            return

        if options['check_only']:
            return

        # 2. Verifica se o usuário existe e é superusuário
        username = options['username']
        password = options['password']

        if not username or not password:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Use --username e --password para testar autenticação')
            )
            return

        self.stdout.write(f'\n👤 Verificando usuário: {username}')
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'   ✅ Usuário encontrado: {user.username}')
            self.stdout.write(f'   📊 is_superuser: {user.is_superuser}')
            self.stdout.write(f'   📊 is_active: {user.is_active}')
            
            if not user.is_superuser:
                self.stdout.write(
                    self.style.WARNING('   ⚠️ Usuário não é superusuário - LicenseBackend não será testado')
                )
                return
                
        except User.DoesNotExist:
            self.stdout.write(f'   ❌ Usuário não encontrado')
            return
        except Exception as e:
            self.stdout.write(f'   ❌ Erro: {e}')
            return

        # 3. Testa LicenseBackend especificamente
        self.stdout.write(f'\n🔍 Testando LicenseBackend:')
        try:
            from core.backends import LicenseBackend
            backend = LicenseBackend()
            
            # Testa autenticação
            authenticated_user = backend.authenticate(None, username=username, password=password)
            
            if authenticated_user:
                if license_valid:
                    self.stdout.write(f'   ✅ Login permitido (licença válida)')
                else:
                    self.stdout.write(f'   ❌ Login permitido (licença inválida - ERRO!)')
            else:
                if license_valid:
                    self.stdout.write(f'   ❌ Login negado (licença válida - ERRO!)')
                else:
                    self.stdout.write(f'   ✅ Login negado (licença inválida - CORRETO!)')
                    
        except Exception as e:
            self.stdout.write(f'   ❌ Erro no LicenseBackend: {e}')

        # 4. Testa todos os backends
        self.stdout.write(f'\n🌐 Testando todos os backends:')
        try:
            from django.contrib.auth import authenticate
            user = authenticate(username=username, password=password)
            
            if user:
                self.stdout.write(f'   ✅ Login bem-sucedido via: {user.backend}')
                if user.backend == 'core.backends.LicenseBackend':
                    self.stdout.write(f'   📊 LicenseBackend foi usado')
                else:
                    self.stdout.write(f'   📊 Outro backend foi usado: {user.backend}')
            else:
                self.stdout.write(f'   ❌ Login falhou')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Erro na autenticação: {e}')

        # 5. Recomendações
        self.stdout.write(f'\n💡 Recomendações:')
        if not license_valid:
            self.stdout.write(f'   • Licença inválida - superusuários devem ser bloqueados')
            self.stdout.write(f'   • Verifique a configuração da licença')
        else:
            self.stdout.write(f'   • Licença válida - superusuários devem conseguir fazer login')
            self.stdout.write(f'   • Sistema funcionando corretamente') 