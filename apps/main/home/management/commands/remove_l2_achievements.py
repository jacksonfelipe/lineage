from django.core.management.base import BaseCommand
from apps.main.home.models import Conquista, ConquistaUsuario

class Command(BaseCommand):
    help = 'Remove conquistas relacionadas ao L2 do banco de dados'

    def handle(self, *args, **options):
        # Lista de códigos de conquistas relacionadas ao L2
        l2_achievement_codes = [
            'primeiro_personagem',
            'primeiro_clan',
            'primeiro_castle',
            'personagem_nivel_50',
            'personagem_nivel_80',
            'personagem_nivel_100',
            'personagem_nobless',
            'personagem_hero',
            'primeiro_subclass',
            'personagem_pvp_100',
            'personagem_pvp_500',
            'personagem_pvp_1000',
            'primeiro_ally',
            'personagem_online_24h',
            'personagem_online_100h',
            'personagem_online_500h',
            'olympiad_participant',
            'olympiad_winner',
            'grandboss_killer',
            'siege_participant',
        ]

        # Remove as conquistas relacionadas ao L2
        for codigo in l2_achievement_codes:
            try:
                conquista = Conquista.objects.filter(codigo=codigo).first()
                if conquista:
                    # Remove primeiro as conquistas dos usuários
                    ConquistaUsuario.objects.filter(conquista=conquista).delete()
                    # Remove a conquista
                    conquista.delete()
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Conquista "{conquista.nome}" removida com sucesso')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'⚠️ Conquista com código "{codigo}" não encontrada')
                    )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Erro ao remover conquista "{codigo}": {e}')
                )

        self.stdout.write(
            self.style.SUCCESS('🎉 Processo de remoção das conquistas L2 concluído!')
        ) 