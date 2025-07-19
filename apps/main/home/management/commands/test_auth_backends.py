from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate, get_user_model
from django.conf import settings
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Testa todos os backends de autenticação configurados'

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
            '--list-backends',
            action='store_true',
            help='Lista todos os backends configurados',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔐 Teste de Backends de Autenticação\n')
        )

        # 1. Lista backends configurados
        self.stdout.write('📋 Backends Configurados:')
        for i, backend in enumerate(settings.AUTHENTICATION_BACKENDS, 1):
            self.stdout.write(f'   {i}. {backend}')

        if options['list_backends']:
            return

        # 2. Testa backends individualmente
        username = options['username']
        password = options['password']

        if not username or not password:
            self.stdout.write(
                self.style.WARNING('\n⚠️ Use --username e --password para testar autenticação')
            )
            return

        self.stdout.write(f'\n🧪 Testando autenticação para usuário: {username}')

        # Testa cada backend individualmente
        for backend in settings.AUTHENTICATION_BACKENDS:
            self.stdout.write(f'\n🔍 Testando backend: {backend}')
            
            try:
                # Importa o backend dinamicamente
                if backend == 'django.contrib.auth.backends.ModelBackend':
                    from django.contrib.auth.backends import ModelBackend
                    backend_instance = ModelBackend()
                elif backend == 'allauth.account.auth_backends.AuthenticationBackend':
                    from allauth.account.auth_backends import AuthenticationBackend
                    backend_instance = AuthenticationBackend()
                elif backend == 'core.backends.LicenseBackend':
                    from core.backends import LicenseBackend
                    backend_instance = LicenseBackend()
                else:
                    self.stdout.write(f'   ❌ Backend desconhecido: {backend}')
                    continue

                # Testa autenticação
                user = backend_instance.authenticate(None, username=username, password=password)
                
                if user:
                    self.stdout.write(f'   ✅ Sucesso: {user.username} (is_superuser: {user.is_superuser})')
                    
                    # Testa get_user
                    retrieved_user = backend_instance.get_user(user.id)
                    if retrieved_user:
                        self.stdout.write(f'   ✅ get_user OK: {retrieved_user.username}')
                    else:
                        self.stdout.write(f'   ❌ get_user falhou')
                        
                else:
                    self.stdout.write(f'   ❌ Falha na autenticação')
                    
            except Exception as e:
                self.stdout.write(f'   ❌ Erro: {e}')

        # 3. Testa autenticação com Django authenticate (todos os backends)
        self.stdout.write(f'\n🌐 Testando authenticate() do Django (todos os backends):')
        try:
            user = authenticate(username=username, password=password)
            if user:
                self.stdout.write(f'   ✅ Sucesso: {user.username} (backend: {user.backend})')
                self.stdout.write(f'   📊 Backend usado: {user.backend}')
            else:
                self.stdout.write(f'   ❌ Falha na autenticação')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro: {e}')

        # 4. Verifica se o usuário existe
        self.stdout.write(f'\n👤 Verificando se o usuário existe no banco:')
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'   ✅ Usuário encontrado: {user.username}')
            self.stdout.write(f'   📊 is_active: {user.is_active}')
            self.stdout.write(f'   📊 is_superuser: {user.is_superuser}')
            self.stdout.write(f'   📊 is_staff: {user.is_staff}')
        except User.DoesNotExist:
            self.stdout.write(f'   ❌ Usuário não encontrado no banco')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro: {e}')

        # 5. Recomendações
        self.stdout.write(f'\n💡 Recomendações:')
        self.stdout.write(f'   • Verifique se o usuário está ativo')
        self.stdout.write(f'   • Verifique se a senha está correta')
        self.stdout.write(f'   • Verifique se o LicenseBackend está funcionando')
        self.stdout.write(f'   • Verifique os logs para mais detalhes') 