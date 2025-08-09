from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from utils.license_manager import check_license_status
from apps.main.licence.manager import license_manager

User = get_user_model()

class Command(BaseCommand):
    help = 'Testa o sistema de bloqueio de login por licença'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Username do superusuário para testar'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Testando sistema de bloqueio de login por licença...\n')
        )

        # 1. Verifica status da licença
        self.stdout.write('📋 Verificando status da licença:')
        try:
            license_status = check_license_status()
            self.stdout.write(f'   Status: {"✅ Válida" if license_status else "❌ Inválida"}')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   Erro ao verificar licença: {e}')
            )
            return

        # 2. Verifica informações detalhadas da licença
        self.stdout.write('\n📊 Informações detalhadas da licença:')
        try:
            license_info = license_manager.get_license_info()
            if license_info:
                self.stdout.write(f'   Tipo: {license_info.get("type", "N/A")}')
                self.stdout.write(f'   Status: {license_info.get("status", "N/A")}')
                self.stdout.write(f'   Domínio: {license_info.get("domain", "N/A")}')
                self.stdout.write(f'   Expira em: {license_info.get("expires_at", "N/A")}')
            else:
                self.stdout.write('   ❌ Nenhuma licença encontrada')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   Erro ao obter informações da licença: {e}')
            )

        # 3. Lista superusuários
        self.stdout.write('\n👥 Superusuários encontrados:')
        superusers = User.objects.filter(is_superuser=True)
        if superusers.exists():
            for user in superusers:
                self.stdout.write(f'   - {user.username} ({user.email})')
        else:
            self.stdout.write('   ❌ Nenhum superusuário encontrado')

        # 4. Testa cenário de bloqueio
        self.stdout.write('\n🚫 Teste de cenário de bloqueio:')
        if license_status:
            self.stdout.write('   ✅ Licença válida - Superusuários podem fazer login')
        else:
            self.stdout.write('   ❌ Licença inválida - Superusuários serão bloqueados')
            
            # Mostra superusuários que seriam afetados
            if superusers.exists():
                self.stdout.write('   Superusuários que seriam bloqueados:')
                for user in superusers:
                    self.stdout.write(f'      - {user.username}')

        # 5. Instruções para teste
        self.stdout.write('\n🧪 Como testar:')
        self.stdout.write('   1. Para simular licença inválida:')
        self.stdout.write('      - Edite uma licença e mude o status para "expired"')
        self.stdout.write('      - Ou modifique a data de expiração para uma data passada')
        self.stdout.write('   2. Tente fazer login com um superusuário')
        self.stdout.write('   3. O login deve ser bloqueado com mensagem de erro')

        self.stdout.write('\n✅ Teste concluído!') 