from django.core.management.base import BaseCommand
from django.conf import settings
from apps.licence.utils import validate_contract_dns
from apps.licence.manager import license_manager


class Command(BaseCommand):
    help = 'Testa a validação DNS de contratos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--contract',
            type=str,
            default='TEST-2024-001',
            help='Número do contrato para testar'
        )
        parser.add_argument(
            '--domain',
            type=str,
            default='localhost',
            help='Domínio para testar'
        )
        parser.add_argument(
            '--create-pro',
            action='store_true',
            help='Cria uma licença PRO de teste'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Teste de Validação DNS")
        self.stdout.write("=" * 50)

        contract_number = options['contract']
        domain = options['domain']
        create_pro = options['create_pro']

        # Verifica se está em modo DEBUG
        self.stdout.write(f"📋 Modo DEBUG: {'✅ Sim' if settings.DEBUG else '❌ Não'}")
        
        if settings.DEBUG:
            self.stdout.write("💡 Em modo DEBUG, a validação DNS será pulada automaticamente")

        # Testa validação DNS
        self.stdout.write(f"\n🧪 Testando validação DNS...")
        self.stdout.write(f"   Contrato: {contract_number}")
        self.stdout.write(f"   Domínio: {domain}")
        
        success, message = validate_contract_dns(contract_number, domain)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f"✅ {message}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ {message}"))

        # Testa criação de licença PRO
        if create_pro:
            self.stdout.write(f"\n🧪 Testando criação de licença PRO...")
            
            success, result = license_manager.create_pro_license(
                domain=domain,
                contact_email="test@example.com",
                company_name="Empresa Teste",
                contact_phone="+55 11 99999-9999",
                contract_number=contract_number,
                skip_dns_validation=False  # Deixa o sistema decidir baseado no DEBUG
            )
            
            if success:
                self.stdout.write(self.style.SUCCESS(f"✅ Licença PRO criada com ID: {result}"))
            else:
                self.stdout.write(self.style.ERROR(f"❌ Erro ao criar licença: {result}"))

        # Informações sobre configuração
        self.stdout.write(f"\n📋 Configuração Atual:")
        self.stdout.write(f"   DNS_TIMEOUT: {settings.LICENSE_CONFIG.get('DNS_TIMEOUT', 10)}s")
        self.stdout.write(f"   ENCRYPTION_KEY: {'✅ Configurada' if settings.LICENSE_CONFIG.get('ENCRYPTION_KEY') else '❌ Não configurada'}")

        # Recomendações
        self.stdout.write(f"\n💡 Recomendações:")
        if settings.DEBUG:
            self.stdout.write("   • Em desenvolvimento, a validação DNS é pulada automaticamente")
            self.stdout.write("   • Para testar validação real, use DEBUG=False")
        else:
            self.stdout.write("   • Em produção, configure os registros DNS corretamente")
            self.stdout.write("   • Verifique se o domínio denky.dev.br está acessível")
        
        self.stdout.write("   • Use --create-pro para testar criação de licença PRO")
        self.stdout.write("   • Use --contract e --domain para testar contratos específicos") 