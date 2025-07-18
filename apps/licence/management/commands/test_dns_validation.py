from django.core.management.base import BaseCommand
from apps.licence.utils import license_validator, generate_dns_record
from django.conf import settings


class Command(BaseCommand):
    help = 'Testa a validação DNS de contratos'

    def add_arguments(self, parser):
        parser.add_argument('contract_number', type=str, help='Número do contrato para testar')
        parser.add_argument('domain', type=str, help='Domínio para testar')

    def handle(self, *args, **options):
        contract_number = options['contract_number']
        domain = options['domain']
        
        self.stdout.write(self.style.SUCCESS(f'Testando validação DNS para contrato: {contract_number}'))
        self.stdout.write(f'Domínio: {domain}')
        
        dns_prefix = settings.LICENSE_CONFIG.get('DNS_TXT_PREFIX', 'pdl-contract')
        txt_record_name = f"{dns_prefix}.{domain}"
        self.stdout.write(f'Registro DNS esperado: {txt_record_name}')
        
        # Testa a validação
        success, message = license_validator.validate_contract_via_dns(contract_number, domain)
        
        if success:
            self.stdout.write(self.style.SUCCESS(f'✅ {message}'))
        else:
            self.stdout.write(self.style.ERROR(f'❌ {message}'))
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('INSTRUÇÕES PARA CONFIGURAR O DNS:')
        self.stdout.write('='*50)
        self.stdout.write(f'1. Acesse o painel de DNS do seu domínio')
        self.stdout.write(f'2. Adicione um registro TXT:')
        self.stdout.write(f'   Nome: {txt_record_name}')
        self.stdout.write(f'   Valor: {contract_number}')
        self.stdout.write(f'3. Aguarde a propagação (pode levar até 24h)')
        self.stdout.write(f'4. Execute este comando novamente para testar')
        
        # Gera exemplo de registro criptografado
        dns_record = generate_dns_record(contract_number, domain, encrypt=True)
        self.stdout.write('\n' + '='*50)
        self.stdout.write('EXEMPLO DE REGISTRO CRIPTOGRAFADO:')
        self.stdout.write('='*50)
        self.stdout.write(f'Nome: {dns_record["name"]}')
        self.stdout.write(f'Tipo: {dns_record["type"]}')
        self.stdout.write(f'Valor: {dns_record["value"]}')
        self.stdout.write(f'TTL: {dns_record["ttl"]}')
        self.stdout.write(f'Criptografado: {dns_record["encrypted"]}') 