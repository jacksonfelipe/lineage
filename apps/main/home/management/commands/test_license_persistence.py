from django.core.management.base import BaseCommand
from django.core.cache import cache
from apps.main.licence.models import License
from apps.main.licence.manager import license_manager
from django.utils import timezone
import time


class Command(BaseCommand):
    help = 'Testa se as mudanças de status da licença persistem'

    def add_arguments(self, parser):
        parser.add_argument(
            '--license-id',
            type=int,
            help='ID da licença para testar'
        )
        parser.add_argument(
            '--new-status',
            type=str,
            choices=['active', 'expired', 'suspended', 'pending'],
            default='suspended',
            help='Novo status para testar'
        )

    def handle(self, *args, **options):
        self.stdout.write("🧪 Teste de Persistência de Status da Licença")
        self.stdout.write("=" * 60)

        # Encontra a licença para testar
        if options['license_id']:
            try:
                license_obj = License.objects.get(id=options['license_id'])
            except License.DoesNotExist:
                self.stdout.write(f"❌ Licença com ID {options['license_id']} não encontrada")
                return
        else:
            license_obj = License.objects.filter(status='active').first()
            if not license_obj:
                self.stdout.write("❌ Nenhuma licença ativa encontrada")
                return

        new_status = options['new_status']
        old_status = license_obj.status

        self.stdout.write(f"\n📋 Licença selecionada:")
        self.stdout.write(f"   ID: {license_obj.id}")
        self.stdout.write(f"   Chave: {license_obj.license_key[:12]}...")
        self.stdout.write(f"   Tipo: {license_obj.get_license_type_display()}")
        self.stdout.write(f"   Status atual: {license_obj.get_status_display()}")
        self.stdout.write(f"   Domínio: {license_obj.domain}")

        # Verifica status inicial via manager
        self.stdout.write(f"\n🔍 Status inicial via LicenseManager:")
        is_valid_initial = license_manager.check_license_status()
        self.stdout.write(f"   Válida: {'✅ Sim' if is_valid_initial else '❌ Não'}")

        # Verifica cache inicial
        self.stdout.write(f"\n🗄️  Cache inicial:")
        cached_license = cache.get('current_license')
        if cached_license:
            self.stdout.write(f"   Status no cache: {cached_license.get_status_display()}")
        else:
            self.stdout.write("   Cache vazio")

        # Altera o status
        self.stdout.write(f"\n🔄 Alterando status para '{new_status}'...")
        license_obj.status = new_status
        license_obj.save()

        # Aguarda um pouco para simular o F5
        time.sleep(2)

        # Verifica se a mudança persistiu
        self.stdout.write(f"\n✅ Verificando se a mudança persistiu:")
        
        # Recarrega do banco
        license_obj.refresh_from_db()
        self.stdout.write(f"   Status no banco: {license_obj.get_status_display()}")
        
        # Verifica via manager
        is_valid_after = license_manager.check_license_status()
        self.stdout.write(f"   Válida via manager: {'✅ Sim' if is_valid_after else '❌ Não'}")
        
        # Verifica cache
        cached_license_after = cache.get('current_license')
        if cached_license_after:
            self.stdout.write(f"   Status no cache: {cached_license_after.get_status_display()}")
        else:
            self.stdout.write("   Cache vazio")

        # Testa múltiplas verificações
        self.stdout.write(f"\n🔄 Testando múltiplas verificações...")
        for i in range(3):
            is_valid = license_manager.check_license_status()
            self.stdout.write(f"   Verificação {i+1}: {'✅ Válida' if is_valid else '❌ Inválida'}")
            time.sleep(1)

        # Restaura o status original
        self.stdout.write(f"\n🔄 Restaurando status original '{old_status}'...")
        license_obj.status = old_status
        license_obj.save()

        # Verifica status final
        self.stdout.write(f"\n✅ Status final:")
        license_obj.refresh_from_db()
        self.stdout.write(f"   Status no banco: {license_obj.get_status_display()}")
        
        is_valid_final = license_manager.check_license_status()
        self.stdout.write(f"   Válida via manager: {'✅ Sim' if is_valid_final else '❌ Não'}")

        # Conclusão
        self.stdout.write(f"\n📊 Resultado do Teste:")
        if license_obj.status == new_status:
            self.stdout.write("   ✅ Mudança de status persistiu no banco")
        else:
            self.stdout.write("   ❌ Mudança de status não persistiu no banco")
            
        if is_valid_initial != is_valid_after:
            self.stdout.write("   ✅ Status da validação mudou corretamente")
        else:
            self.stdout.write("   ⚠️  Status da validação não mudou como esperado")

        self.stdout.write(f"\n💡 Recomendações:")
        self.stdout.write("   • Se a mudança não persistir, verifique se há processos automáticos")
        self.stdout.write("   • Monitore os logs para ver se há reativação automática")
        self.stdout.write("   • Use o comando debug_license_status para mais detalhes") 