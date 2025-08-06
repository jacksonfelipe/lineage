from django.core.management.base import BaseCommand
from apps.lineage.server.models import IndexConfig


class Command(BaseCommand):
    help = 'Cria a configuração inicial do IndexConfig se ela não existir'

    def handle(self, *args, **options):
        if IndexConfig.objects.exists():
            self.stdout.write(
                self.style.WARNING('Configuração do IndexConfig já existe.')
            )
            return

        config = IndexConfig.objects.create(
            nome_servidor="Lineage 2 L2JPremium",
            descricao_servidor="Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna.",
            link_patch="https://L2JPremium.com/",
            link_cliente="https://L2JPremium.com/",
            link_discord="https://L2JPremium.com/",
            trailer_video_id="CsNutvmrHIA?si=2lF1z1jPFkf8uGJB",
            jogadores_online_texto="jogadores online Agora"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Configuração do IndexConfig criada com sucesso: {config.nome_servidor}'
            )
        ) 