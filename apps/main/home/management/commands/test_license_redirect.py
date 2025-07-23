from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from utils.license_manager import check_license_status
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o redirecionamento baseado no tipo de usuário quando a licença for inválida'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Nome do usuário para testar'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Senha do usuário'
        )
        parser.add_argument(
            '--simulate-invalid',
            action='store_true',
            help='Simula licença inválida para teste'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Teste de Redirecionamento por Tipo de Usuário")
        self.stdout.write("=" * 60)

        username = options.get('username')
        password = options.get('password')
        simulate_invalid = options.get('simulate_invalid')

        # Verifica status atual da licença
        current_status = check_license_status()
        self.stdout.write(f"📋 Status atual da licença: {'✅ Válida' if current_status else '❌ Inválida'}")

        if simulate_invalid:
            self.stdout.write("⚠️  Simulando licença inválida para teste...")
            # Aqui você pode adicionar lógica para simular licença inválida temporariamente

        if not username or not password:
            self.stdout.write("❌ Usuário e senha são obrigatórios")
            self.stdout.write("Uso: python manage.py test_license_redirect --username admin --password senha")
            return

        # Verifica se o usuário existe
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f"👤 Usuário encontrado: {user.username} (is_superuser: {user.is_superuser})")
        except User.DoesNotExist:
            self.stdout.write(f"❌ Usuário '{username}' não encontrado")
            return

        # Testa login e redirecionamento
        client = Client()
        
        self.stdout.write("\n🧪 Testando login e redirecionamento...")
        
        # Tenta fazer login
        login_success = client.login(username=username, password=password)
        
        if login_success:
            self.stdout.write(f"✅ Login bem-sucedido para {username}")
            
            # Testa acesso a uma página protegida
            response = client.get('/')
            
            self.stdout.write(f"📊 Status da resposta: {response.status_code}")
            
            if response.status_code == 302:  # Redirecionamento
                redirect_url = response.url
                self.stdout.write(f"🔄 Redirecionado para: {redirect_url}")
                
                if '/public/maintenance/' in redirect_url:
                    self.stdout.write("🎯 Usuário comum redirecionado para MANUTENÇÃO (CORRETO!)")
                elif '/public/license-expired/' in redirect_url:
                    self.stdout.write("🎯 Superusuário redirecionado para LICENÇA EXPIRADA (CORRETO!)")
                else:
                    self.stdout.write(f"❓ Redirecionamento inesperado: {redirect_url}")
            else:
                self.stdout.write("✅ Acesso permitido - licença válida")
                
        else:
            self.stdout.write(f"❌ Falha no login para {username}")
            
            # Verifica se a falha foi devido à licença
            if not check_license_status():
                self.stdout.write("🔒 Login bloqueado devido à licença inválida")
                
                # Testa acesso direto às páginas
                self.stdout.write("\n🧪 Testando acesso direto às páginas...")
                
                # Testa página de manutenção
                maintenance_response = client.get('/public/maintenance/')
                self.stdout.write(f"📄 Página de manutenção: {maintenance_response.status_code}")
                
                # Testa página de licença expirada
                license_response = client.get('/public/license-expired/')
                self.stdout.write(f"📄 Página de licença expirada: {license_response.status_code}")
                
                if user.is_superuser:
                    self.stdout.write("👑 Usuário é superusuário - deve ver página de licença expirada")
                else:
                    self.stdout.write("👤 Usuário comum - deve ver página de manutenção")
            else:
                self.stdout.write("❌ Falha no login por credenciais inválidas")

        self.stdout.write("\n💡 Recomendações:")
        self.stdout.write("   • Use --simulate-invalid para testar com licença inválida")
        self.stdout.write("   • Monitore os logs para verificar o comportamento")
        self.stdout.write("   • Teste com usuários comuns e superusuários") 