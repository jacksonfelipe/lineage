from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.hashers import check_password
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class Command(BaseCommand):
    help = 'Verifica se um usuário existe e suas credenciais'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            required=True,
            help='Username para verificar',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha para testar',
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Cria o usuário se não existir',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('👤 Verificação de Usuário\n')
        )

        username = options['username']
        password = options['password']
        create = options['create']

        # 1. Verifica se o usuário existe
        self.stdout.write(f'🔍 Verificando usuário: {username}')
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'   ✅ Usuário encontrado: {user.username}')
            self.stdout.write(f'   📊 Email: {user.email}')
            self.stdout.write(f'   📊 is_active: {user.is_active}')
            self.stdout.write(f'   📊 is_superuser: {user.is_superuser}')
            self.stdout.write(f'   📊 is_staff: {user.is_staff}')
            self.stdout.write(f'   📊 Date joined: {user.date_joined}')
            
        except User.DoesNotExist:
            self.stdout.write(f'   ❌ Usuário não encontrado: {username}')
            
            if create and password:
                self.stdout.write(f'   🛠️ Criando usuário...')
                try:
                    user = User.objects.create_user(
                        username=username,
                        email=f'{username}@example.com',
                        password=password,
                        is_superuser=True,
                        is_staff=True
                    )
                    self.stdout.write(f'   ✅ Usuário criado com sucesso: {user.username}')
                except Exception as e:
                    self.stdout.write(f'   ❌ Erro ao criar usuário: {e}')
                    return
            else:
                self.stdout.write(f'   💡 Use --create --password para criar o usuário')
                return

        # 2. Testa autenticação se senha fornecida
        if password:
            self.stdout.write(f'\n🔐 Testando autenticação:')
            
            # Testa com check_password
            if check_password(password, user.password):
                self.stdout.write(f'   ✅ Senha correta (check_password)')
            else:
                self.stdout.write(f'   ❌ Senha incorreta (check_password)')
            
            # Testa com authenticate
            authenticated_user = authenticate(username=username, password=password)
            if authenticated_user:
                self.stdout.write(f'   ✅ Autenticação bem-sucedida (authenticate)')
                self.stdout.write(f'   📊 Backend usado: {authenticated_user.backend}')
            else:
                self.stdout.write(f'   ❌ Autenticação falhou (authenticate)')
                
                # Verifica se o usuário está ativo
                if not user.is_active:
                    self.stdout.write(f'   ⚠️ Usuário não está ativo')
                
                # Verifica se a senha está correta
                if not check_password(password, user.password):
                    self.stdout.write(f'   ⚠️ Senha incorreta')

        # 3. Lista todos os usuários
        self.stdout.write(f'\n📋 Todos os usuários no sistema:')
        users = User.objects.all().order_by('username')
        for u in users:
            status = "✅" if u.is_active else "❌"
            superuser = "👑" if u.is_superuser else "👤"
            self.stdout.write(f'   {status} {superuser} {u.username} ({u.email})')

        # 4. Recomendações
        self.stdout.write(f'\n💡 Recomendações:')
        if not user.is_active:
            self.stdout.write(f'   • Ative o usuário: user.is_active = True')
        if not user.is_superuser:
            self.stdout.write(f'   • Torne superusuário: user.is_superuser = True')
        if password and not check_password(password, user.password):
            self.stdout.write(f'   • Redefina a senha: user.set_password("nova_senha")') 