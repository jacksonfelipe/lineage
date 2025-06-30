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
            nome_servidor="Lineage 2 PDL",
            descricao_servidor="Onde Lendas Nascem, Heróis Lutam e a Glória É Eterna.",
            link_patch="https://pdl.denky.dev.br/",
            link_cliente="https://pdl.denky.dev.br/",
            link_discord="https://pdl.denky.dev.br/",
            trailer_video_id="CsNutvmrHIA?si=2lF1z1jPFkf8uGJB",
            jogadores_online_texto="jogadores online Agora"
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Configuração do IndexConfig criada com sucesso: {config.nome_servidor}'
            )
        ) 