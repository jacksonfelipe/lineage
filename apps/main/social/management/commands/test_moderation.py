"""
Comando Django para testar o sistema de moderação
"""

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _
from django.contrib.auth import get_user_model
from apps.main.social.models import ContentFilter, Post, Report
import time

User = get_user_model()


class Command(BaseCommand):
    help = 'Testa o sistema de moderação com exemplos práticos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-data',
            action='store_true',
            help='Criar dados de teste'
        )
        parser.add_argument(
            '--performance',
            action='store_true',
            help='Executar teste de performance'
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🛡️  TESTE DO SISTEMA DE MODERAÇÃO')
        )
        self.stdout.write('=' * 60)
        
        # Executar testes principais
        self.test_content_filters()
        
        if options['performance']:
            self.test_performance()
        
        if options['create_test_data']:
            self.create_test_data()
        
        self.generate_report()
        
        self.stdout.write('\n' + self.style.SUCCESS('✅ Testes concluídos!'))

    def test_content_filters(self):
        """Testa os filtros de conteúdo"""
        self.stdout.write('\n🧪 TESTANDO FILTROS DE CONTEÚDO')
        self.stdout.write('-' * 40)
        
        # Casos de teste
        test_cases = [
            ("Ganhe dinheiro fácil! Clique aqui agora!", "SPAM_COMERCIAL"),
            ("Que merda de situação!", "PALAVRAO_MODERADO"),
            ("Vem ver minhas nudes no link", "CONTEUDO_ADULTO"),
            ("Acesse bit.ly/link-suspeito para ganhar prêmio", "URL_SUSPEITA"),
            ("Esses negros não prestam mesmo", "DISCURSO_ODIO"),
            ("Vacina mata mais que cura, não tomem!", "FAKE_NEWS"),
            ("ATENÇÃO URGENTE TODOS LEIAM AGORA MESMO", "CAPS_EXCESSIVO"),
            ("PIX grátis! Auxílio emergencial liberado", "GOLPE_BRASILEIRO"),
            ("Boa tarde pessoal! Como estão hoje?", "CONTEUDO_NORMAL"),
        ]
        
        active_filters = ContentFilter.objects.filter(is_active=True)
        self.stdout.write(f'📊 Filtros ativos: {active_filters.count()}')
        
        if not active_filters.exists():
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  Nenhum filtro ativo encontrado!\n'
                    'Execute: python manage.py setup_moderation'
                )
            )
            return
        
        for content, category in test_cases:
            self.stdout.write(f'\n🔍 {category}')
            self.stdout.write(f'   Texto: "{content}"')
            
            matched_filters = []
            for content_filter in active_filters:
                try:
                    if content_filter.matches_content(content):
                        matched_filters.append({
                            'name': content_filter.name,
                            'action': content_filter.action,
                            'type': content_filter.filter_type
                        })
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Erro no filtro {content_filter.name}: {e}')
                    )
            
            if matched_filters:
                self.stdout.write(
                    self.style.WARNING(f'   ⚠️  FILTRADO! ({len(matched_filters)} filtros)')
                )
                for match in matched_filters:
                    self.stdout.write(f'      • {match["name"]} → {match["action"]}')
            else:
                self.stdout.write(self.style.SUCCESS('   ✅ APROVADO'))

    def test_performance(self):
        """Testa performance dos filtros"""
        self.stdout.write('\n⚡ TESTE DE PERFORMANCE')
        self.stdout.write('-' * 30)
        
        test_content = "Este é um texto normal para testar a velocidade dos filtros."
        active_filters = ContentFilter.objects.filter(is_active=True)
        iterations = 100
        
        if not active_filters.exists():
            self.stdout.write(self.style.WARNING('Nenhum filtro para testar'))
            return
        
        start_time = time.time()
        
        for i in range(iterations):
            for content_filter in active_filters:
                try:
                    content_filter.matches_content(test_content)
                except Exception:
                    pass  # Ignorar erros durante teste de performance
        
        end_time = time.time()
        total_time = end_time - start_time
        total_checks = iterations * active_filters.count()
        
        self.stdout.write(f'📊 Resultados:')
        self.stdout.write(f'   • Filtros testados: {active_filters.count()}')
        self.stdout.write(f'   • Iterações: {iterations}')
        self.stdout.write(f'   • Tempo total: {total_time:.3f}s')
        if total_time > 0:
            self.stdout.write(f'   • Verificações/segundo: {int(total_checks / total_time)}')
        else:
            self.stdout.write(f'   • Verificações/segundo: ∞ (muito rápido!)')

    def create_test_data(self):
        """Cria dados de teste"""
        self.stdout.write('\n📝 CRIANDO DADOS DE TESTE')
        self.stdout.write('-' * 30)
        
        # Criar usuário de teste
        test_user, created = User.objects.get_or_create(
            username='moderacao_test',
            defaults={
                'email': 'test.moderacao@example.com',
                'first_name': 'Test',
                'last_name': 'Moderação'
            }
        )
        
        if created:
            self.stdout.write('✅ Usuário de teste criado')
        else:
            self.stdout.write('ℹ️  Usando usuário de teste existente')
        
        # Posts de teste que devem ser filtrados
        test_posts = [
            "Compre agora com desconto! Link: bit.ly/oferta",
            "Que porra é essa situação?",
            "Vem ver meu OnlyFans no link da bio",
            "ATENÇÃO URGENTE! CLIQUE AQUI AGORA!",
            "PIX grátis liberado pelo governo",
        ]
        
        created_posts = 0
        for content in test_posts:
            post, created = Post.objects.get_or_create(
                author=test_user,
                content=content,
                defaults={'is_public': True}
            )
            if created:
                created_posts += 1
                self.stdout.write(f'📄 Post criado: "{content[:30]}..."')
        
        self.stdout.write(f'✅ {created_posts} novos posts de teste criados')

    def generate_report(self):
        """Gera relatório do sistema"""
        self.stdout.write('\n📋 RELATÓRIO DO SISTEMA')
        self.stdout.write('-' * 30)
        
        # Estatísticas gerais
        total_filters = ContentFilter.objects.count()
        active_filters = ContentFilter.objects.filter(is_active=True).count()
        total_reports = Report.objects.count()
        pending_reports = Report.objects.filter(status='pending').count()
        total_posts = Post.objects.count()
        
        self.stdout.write(f'📊 Estatísticas:')
        self.stdout.write(f'   • Filtros configurados: {total_filters}')
        self.stdout.write(f'   • Filtros ativos: {active_filters}')
        self.stdout.write(f'   • Posts no sistema: {total_posts}')
        self.stdout.write(f'   • Denúncias totais: {total_reports}')
        self.stdout.write(f'   • Denúncias pendentes: {pending_reports}')
        
        # Filtros por tipo
        if active_filters > 0:
            self.stdout.write(f'\n🎯 Filtros por Tipo:')
            filter_types = ContentFilter.objects.filter(is_active=True).values_list('filter_type', flat=True)
            type_counts = {}
            for f_type in filter_types:
                type_counts[f_type] = type_counts.get(f_type, 0) + 1
            
            for f_type, count in type_counts.items():
                self.stdout.write(f'   • {f_type}: {count}')
            
            # Filtros por ação
            self.stdout.write(f'\n⚡ Filtros por Ação:')
            actions = ContentFilter.objects.filter(is_active=True).values_list('action', flat=True)
            action_counts = {}
            for action in actions:
                action_counts[action] = action_counts.get(action, 0) + 1
            
            for action, count in action_counts.items():
                self.stdout.write(f'   • {action}: {count}')
        
        # Recomendações
        self.stdout.write(f'\n💡 Recomendações:')
        
        if total_filters == 0:
            self.stdout.write('   • Execute: python manage.py setup_moderation')
        
        if active_filters < 5:
            self.stdout.write('   • Considere ativar mais filtros para melhor proteção')
        
        if pending_reports > 0:
            self.stdout.write(f'   • Revisar {pending_reports} denúncias pendentes')
        
        self.stdout.write('   • Monitorar logs de moderação regularmente')
        self.stdout.write('   • Acessar /admin/social/contentfilter/ para gerenciar')
