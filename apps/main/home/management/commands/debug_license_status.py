from django.core.management.base import BaseCommand
from django.core.cache import cache
from django.conf import settings
from apps.licence.models import License
from apps.licence.manager import license_manager
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Diagnostica problemas com o status da licença'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Limpa o cache de licença'
        )
        parser.add_argument(
            '--check-all',
            action='store_true',
            help='Verifica todas as licenças no sistema'
        )

    def handle(self, *args, **options):
        self.stdout.write("🔍 Diagnóstico de Status da Licença")
        self.stdout.write("=" * 50)

        # Limpa cache se solicitado
        if options['clear_cache']:
            cache_key = 'current_license'
            cache.delete(cache_key)
            self.stdout.write("🗑️  Cache de licença limpo")

        # Verifica configurações
        self.stdout.write(f"\n📋 Configurações:")
        self.stdout.write(f"   DEBUG: {settings.DEBUG}")
        self.stdout.write(f"   Cache Timeout: {settings.LICENSE_CONFIG.get('CACHE_TIMEOUT', 3600)}s")
        self.stdout.write(f"   Verification Interval: {settings.LICENSE_CONFIG.get('VERIFICATION_INTERVAL', 3600)}s")

        # Verifica todas as licenças
        self.stdout.write(f"\n📋 Todas as Licenças no Sistema:")
        licenses = License.objects.all().order_by('-created_at')
        
        if not licenses.exists():
            self.stdout.write("   ❌ Nenhuma licença encontrada")
            return

        for i, license in enumerate(licenses, 1):
            self.stdout.write(f"\n   {i}. {license.license_key[:12]}...")
            self.stdout.write(f"      Tipo: {license.get_license_type_display()}")
            self.stdout.write(f"      Status: {license.get_status_display()}")
            self.stdout.write(f"      Domínio: {license.domain}")
            self.stdout.write(f"      Criada: {license.created_at.strftime('%d/%m/%Y %H:%M:%S')}")
            self.stdout.write(f"      Ativada: {license.activated_at.strftime('%d/%m/%Y %H:%M:%S') if license.activated_at else 'Nunca'}")
            if license.expires_at:
                self.stdout.write(f"      Expira: {license.expires_at.strftime('%d/%m/%Y %H:%M:%S')}")
                if license.expires_at < timezone.now():
                    self.stdout.write(f"      ⚠️  EXPIRADA!")
            self.stdout.write(f"      Verificações: {license.verification_count}")
            if license.last_verification:
                self.stdout.write(f"      Última verificação: {license.last_verification.strftime('%d/%m/%Y %H:%M:%S')}")

        # Verifica licença atual via manager
        self.stdout.write(f"\n🔍 Verificação via LicenseManager:")
        current_license = license_manager.get_current_license()
        
        if current_license:
            self.stdout.write(f"   ✅ Licença atual encontrada: {current_license.license_key[:12]}...")
            self.stdout.write(f"   Status: {current_license.get_status_display()}")
            
            # Verifica status
            is_valid = license_manager.check_license_status()
            self.stdout.write(f"   Válida: {'✅ Sim' if is_valid else '❌ Não'}")
        else:
            self.stdout.write("   ❌ Nenhuma licença atual encontrada")

        # Verifica cache
        self.stdout.write(f"\n🗄️  Status do Cache:")
        cache_key = 'current_license'
        cached_license = cache.get(cache_key)
        
        if cached_license:
            self.stdout.write(f"   ✅ Cache encontrado: {cached_license.license_key[:12]}...")
            self.stdout.write(f"   Status no cache: {cached_license.get_status_display()}")
        else:
            self.stdout.write("   ❌ Cache vazio")

        # Verifica se há processos automáticos
        self.stdout.write(f"\n⚙️  Processos Automáticos:")
        
        # Verifica se há verificação remota
        if current_license:
            should_verify = license_manager._should_verify_remotely(current_license)
            self.stdout.write(f"   Verificação remota necessária: {'✅ Sim' if should_verify else '❌ Não'}")
            
            if should_verify:
                self.stdout.write("   ⚠️  Isso pode estar causando reativação automática!")

        # Verifica se há verificação de expiração automática
        if current_license and current_license.license_type == 'pro' and current_license.expires_at:
            if current_license.expires_at > timezone.now():
                self.stdout.write("   ✅ Licença PRO não expirou")
            else:
                self.stdout.write("   ⚠️  Licença PRO expirou - pode ser reativada automaticamente")

        # Recomendações
        self.stdout.write(f"\n💡 Recomendações:")
        self.stdout.write("   • Use --clear-cache para limpar o cache")
        self.stdout.write("   • Verifique se há processos Celery rodando")
        self.stdout.write("   • Monitore os logs para ver verificações automáticas")
        self.stdout.write("   • Verifique se a data de expiração está correta")
        
        if current_license and current_license.status == 'active':
            self.stdout.write("   • Para testar bloqueio, mude o status para 'suspended' ou 'expired'")
            self.stdout.write("   • Evite usar 'pending' pois pode ser reativado automaticamente") 