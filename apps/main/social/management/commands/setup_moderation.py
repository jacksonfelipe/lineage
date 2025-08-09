from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from apps.main.social.models import ContentFilter


class Command(BaseCommand):
    help = 'Configura filtros padrão de moderação abrangentes'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Configurando filtros padrão de moderação abrangentes...')
        )

        # ============================================================================
        # FILTROS DE SPAM E MARKETING
        # ============================================================================
        spam_filters = [
            {
                'name': 'Spam - Palavras Comerciais',
                'filter_type': 'keyword',
                'pattern': 'buy sell cheap discount free money earn rich business opportunity make money click here visit now limited time act now urgent',
                'action': 'flag',
                'description': 'Detecta palavras comumente usadas em spam comercial',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Medicamentos e Saúde',
                'filter_type': 'keyword',
                'pattern': 'viagra cialis levitra pharmacy medicine online pills prescription drugs weight loss diet supplement testosterone',
                'action': 'auto_hide',
                'description': 'Detecta spam relacionado a medicamentos e suplementos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Jogos de Azar e Apostas',
                'filter_type': 'keyword',
                'pattern': 'casino poker lottery bet gambling slots jackpot bingo roulette blackjack sportingbet betfair',
                'action': 'auto_hide',
                'description': 'Detecta conteúdo relacionado a jogos de azar e apostas',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Spam - Esquemas Financeiros',
                'filter_type': 'keyword',
                'pattern': 'pyramid scheme ponzi investment bitcoin crypto trading forex binary options get rich quick passive income',
                'action': 'flag',
                'description': 'Detecta esquemas financeiros suspeitos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE LINGUAGEM INADEQUADA (PORTUGUÊS)
        # ============================================================================
        profanity_filters = [
            {
                'name': 'Palavrões - Português (Moderado)',
                'filter_type': 'keyword',
                'pattern': 'porra merda caralho cacete buceta puta filho da puta fdp',
                'action': 'flag',
                'description': 'Detecta palavrões comuns em português (nível moderado)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Palavrões - Português (Severo)',
                'filter_type': 'keyword',
                'pattern': 'viado bicha gay de merda cu cuzão arrombado',
                'action': 'auto_hide',
                'description': 'Detecta palavrões ofensivos e discriminatórios',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Linguagem Inadequada - Expressões com Símbolos',
                'filter_type': 'regex',
                'pattern': r'\b(p\*rra|m\*rda|c\*ralho|p\*ta|f\*ck|sh\*t|b\*tch|a\*shole)\b',
                'action': 'flag',
                'description': 'Detecta expressões inadequadas com asteriscos ou símbolos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            }
        ]

        # ============================================================================
        # FILTROS CONTRA PORNOGRAFIA E CONTEÚDO ADULTO
        # ============================================================================
        adult_content_filters = [
            {
                'name': 'Conteúdo Pornográfico - Palavras Explícitas',
                'filter_type': 'keyword',
                'pattern': 'porn porno pornografia sex sexo nude nudes naked pelada gostosa bunduda peituda',
                'action': 'auto_hide',
                'description': 'Detecta conteúdo pornográfico explícito',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Conteúdo Adulto - Termos Sexuais',
                'filter_type': 'keyword',
                'pattern': 'masturbation masturbação orgasm orgasmo ejaculation ejaculação penetration penetração oral anal',
                'action': 'auto_hide',
                'description': 'Detecta termos sexuais explícitos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Sites Pornográficos',
                'filter_type': 'regex',
                'pattern': r'(pornhub|xvideos|redtube|youporn|xhamster|xnxx|brazzers|onlyfans)',
                'action': 'auto_delete',
                'description': 'Detecta links para sites pornográficos conhecidos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE URLS E SITES SUSPEITOS
        # ============================================================================
        suspicious_urls_filters = [
            {
                'name': 'Encurtadores de URL Suspeitos',
                'filter_type': 'regex',
                'pattern': r'http[s]?://(bit\.ly|tinyurl|goo\.gl|t\.co|short\.link|tiny\.cc|ow\.ly|is\.gd)',
                'action': 'flag',
                'description': 'Detecta URLs de encurtadores que podem ocultar conteúdo malicioso',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Sites de Phishing e Malware',
                'filter_type': 'regex',
                'pattern': r'(\.tk|\.ml|\.ga|\.cf|tempmail|guerrillamail|10minutemail)',
                'action': 'auto_hide',
                'description': 'Detecta domínios suspeitos frequentemente usados para phishing',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Múltiplas URLs em Sequência',
                'filter_type': 'regex',
                'pattern': r'http[s]?://[^\s]+.*http[s]?://[^\s]+.*http[s]?://[^\s]+',
                'action': 'flag',
                'description': 'Detecta posts com muitas URLs (possível spam)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Domínios Suspeitos de Criptomoedas',
                'filter_type': 'regex',
                'pattern': r'(free-bitcoin|btc-generator|crypto-giveaway|bitcoin-doubler|coin-flip)',
                'action': 'auto_hide',
                'description': 'Detecta sites fraudulentos relacionados a criptomoedas',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS CONTRA DISCURSO DE ÓDIO E DISCRIMINAÇÃO
        # ============================================================================
        hate_speech_filters = [
            {
                'name': 'Discurso de Ódio - Racial',
                'filter_type': 'keyword',
                'pattern': 'nigger negro de merda macaco preto fedorento',
                'action': 'auto_delete',
                'description': 'Detecta linguagem racista e discriminatória',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Discurso de Ódio - Homofóbico',
                'filter_type': 'keyword',
                'pattern': 'viado nojento gay de merda sapatão traveco',
                'action': 'auto_delete',
                'description': 'Detecta linguagem homofóbica e transfóbica',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            },
            {
                'name': 'Discurso de Ódio - Religioso',
                'filter_type': 'keyword',
                'pattern': 'crente fanático islamita terrorista judeu sujo',
                'action': 'auto_hide',
                'description': 'Detecta linguagem discriminatória religiosa',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': True
            }
        ]

        # ============================================================================
        # FILTROS CONTRA FAKE NEWS E DESINFORMAÇÃO
        # ============================================================================
        misinformation_filters = [
            {
                'name': 'Fake News - Saúde',
                'filter_type': 'keyword',
                'pattern': 'vacina mata autismo cura cancer milagre remedio caseiro covid fake',
                'action': 'flag',
                'description': 'Detecta possível desinformação médica',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Teorias da Conspiração',
                'filter_type': 'keyword',
                'pattern': 'terra plana illuminati nova ordem mundial chip 5g controlam mente',
                'action': 'flag',
                'description': 'Detecta teorias da conspiração comuns',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS DE COMPORTAMENTO SUSPEITO
        # ============================================================================
        behavior_filters = [
            {
                'name': 'Conteúdo Repetitivo',
                'filter_type': 'regex',
                'pattern': r'(.{15,})\1{2,}',
                'action': 'flag',
                'description': 'Detecta conteúdo repetitivo (possível spam)',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'CAPS Excessivo',
                'filter_type': 'regex',
                'pattern': r'[A-Z]{15,}',
                'action': 'flag',
                'description': 'Detecta texto em maiúsculas excessivo',
                'case_sensitive': True,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Excesso de Emojis',
                'filter_type': 'regex',
                'pattern': r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]{10,}',
                'action': 'flag',
                'description': 'Detecta uso excessivo de emojis',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Informações Pessoais',
                'filter_type': 'regex',
                'pattern': r'(\d{3}[-.]?\d{3}[-.]?\d{3}[-.]?\d{2}|\(\d{2}\)\s?\d{4,5}[-.]?\d{4}|whatsapp|telefone|celular)',
                'action': 'flag',
                'description': 'Detecta possível compartilhamento de informações pessoais',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # ============================================================================
        # FILTROS ESPECÍFICOS PARA BRASIL
        # ============================================================================
        brazil_specific_filters = [
            {
                'name': 'Golpes Brasileiros',
                'filter_type': 'keyword',
                'pattern': 'pix gratis auxilio emergencial bolsa familia cpf liberado fgts saque',
                'action': 'flag',
                'description': 'Detecta golpes comuns no Brasil',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            },
            {
                'name': 'Sites de Apostas Brasileiros',
                'filter_type': 'keyword',
                'pattern': 'blaze crash mines aviator fortune tiger jogo do bicho bets',
                'action': 'flag',
                'description': 'Detecta referências a sites de apostas populares no Brasil',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        ]

        # Combinar todos os filtros
        all_filters = (spam_filters + profanity_filters + adult_content_filters + 
                      suspicious_urls_filters + hate_speech_filters + misinformation_filters + 
                      behavior_filters + brazil_specific_filters)

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

        # Criar filtro de padrão de spam automático
        spam_pattern_filter, created = ContentFilter.objects.get_or_create(
            name='Padrão de Spam Automático',
            defaults={
                'filter_type': 'spam_pattern',
                'pattern': 'auto',
                'action': 'flag',
                'description': 'Detecta automaticamente padrões comuns de spam usando algoritmos internos',
                'case_sensitive': False,
                'apply_to_posts': True,
                'apply_to_comments': True,
                'apply_to_usernames': False
            }
        )

        if created:
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS('✓ Criado filtro de padrão de spam automático')
            )

        # Mensagem final com estatísticas
        total_active = ContentFilter.objects.filter(is_active=True).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'🛡️  SISTEMA DE MODERAÇÃO CONFIGURADO COM SUCESSO!\n'
                f'{"="*60}\n'
                f'📊 Estatísticas:\n'
                f'   • Filtros criados: {created_count}\n'
                f'   • Filtros atualizados: {updated_count}\n'
                f'   • Total de filtros ativos: {total_active}\n\n'
                f'🎯 Categorias de filtros configuradas:\n'
                f'   • Spam e Marketing\n'
                f'   • Palavrões e Linguagem Inadequada\n'
                f'   • Conteúdo Pornográfico e Adulto\n'
                f'   • URLs e Sites Suspeitos\n'
                f'   • Discurso de Ódio e Discriminação\n'
                f'   • Fake News e Desinformação\n'
                f'   • Comportamentos Suspeitos\n'
                f'   • Filtros Específicos do Brasil\n\n'
                f'🔧 Próximos passos:\n'
                f'   1. Acesse o painel admin para ajustar filtros\n'
                f'   2. Configure ações automáticas conforme necessário\n'
                f'   3. Monitore logs de moderação regularmente\n'
                f'   4. Treine sua equipe de moderação\n\n'
                f'📋 Acesse: /admin/social/contentfilter/ para gerenciar\n'
                f'{"="*60}'
            )
        )
