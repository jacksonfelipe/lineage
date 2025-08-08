from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter


class Command(BaseCommand):
    help = 'Configura filtros padrão de moderação'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Configurando filtros padrão de moderação...')
        )

        # Filtros de spam
        spam_filters = [
            {
                'name': 'Spam - Palavras Comerciais',
                'filter_type': 'keyword',
                'pattern': 'buy sell cheap discount free money earn rich',
                'action': 'flag',
                'description': 'Detecta palavras comumente usadas em spam comercial',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Medicamentos',
                'filter_type': 'keyword',
                'pattern': 'viagra cialis pharmacy medicine',
                'action': 'auto_hide',
                'description': 'Detecta spam relacionado a medicamentos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Jogos de Azar',
                'filter_type': 'keyword',
                'pattern': 'casino poker lottery bet gambling',
                'action': 'flag',
                'description': 'Detecta conteúdo relacionado a jogos de azar',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Filtros de linguagem inadequada
        language_filters = [
            {
                'name': 'Linguagem Inadequada - Palavrões',
                'filter_type': 'keyword',
                'pattern': 'palavrão1 palavrão2 palavrão3',  # Substituir por palavras reais
                'action': 'auto_hide',
                'description': 'Detecta linguagem inadequada',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Linguagem Inadequada - Expressões',
                'filter_type': 'regex',
                'pattern': r'\b(f\*\*k|s\*\*t|b\*\*ch|a\*\*hole)\b',
                'action': 'flag',
                'description': 'Detecta expressões inadequadas com asteriscos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Filtros de URLs suspeitas
        url_filters = [
            {
                'name': 'URLs Suspeitas',
                'filter_type': 'regex',
                'pattern': r'http[s]?://(bit\.ly|tinyurl|goo\.gl|t\.co)',
                'action': 'flag',
                'description': 'Detecta URLs de encurtadores suspeitos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Múltiplas URLs',
                'filter_type': 'regex',
                'pattern': r'http[s]?://.*http[s]?://.*http[s]?://',
                'action': 'flag',
                'description': 'Detecta posts com muitas URLs (possível spam)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Filtros de conteúdo repetitivo
        repetitive_filters = [
            {
                'name': 'Conteúdo Repetitivo',
                'filter_type': 'regex',
                'pattern': r'(.{10,})\1{2,}',
                'action': 'flag',
                'description': 'Detecta conteúdo repetitivo',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Filtros de CAPS excessivo
        caps_filters = [
            {
                'name': 'CAPS Excessivo',
                'filter_type': 'regex',
                'pattern': r'[A-Z]{10,}',
                'action': 'flag',
                'description': 'Detecta texto em maiúsculas excessivo',
                'case_sensitive': True,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Combinar todos os filtros
        all_filters = spam_filters + language_filters + url_filters + repetitive_filters + caps_filters

        created_count = 0
        updated_count = 0

        for filter_data in all_filters:
            filter_obj, created = ContentFilter.objects.get_or_create(
                name=filter_data['name'],
                defaults=filter_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Criado filtro: {filter_data["name"]}')
                )
            else:
                # Atualizar filtro existente
                for key, value in filter_data.items():
                    setattr(filter_obj, key, value)
                filter_obj.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'↻ Atualizado filtro: {filter_data["name"]}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\nConfiguração concluída!\n'
                f'Filtros criados: {created_count}\n'
                f'Filtros atualizados: {updated_count}\n'
                f'Total de filtros ativos: {ContentFilter.objects.filter(is_active=True).count()}'
            )
        )

        # Criar filtros de padrão de spam
        spam_pattern_filter, created = ContentFilter.objects.get_or_create(
            name='Padrão de Spam Automático',
            defaults={
                'filter_type': 'spam_pattern',
                'pattern': 'auto',
                'action': 'flag',
                'description': 'Detecta automaticamente padrões comuns de spam',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS('✓ Criado filtro de padrão de spam automático')
            )

        self.stdout.write(
            self.style.SUCCESS(
                '\nFiltros configurados com sucesso! '
                'Acesse o painel de moderação para gerenciar os filtros.'
            )
        )
