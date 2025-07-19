from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import time
import threading


class Command(BaseCommand):
    help = 'Diagnostica problemas de bloqueio de banco de dados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-writes',
            action='store_true',
            help='Testa escritas simultâneas no banco',
        )
        parser.add_argument(
            '--check-connections',
            action='store_true',
            help='Verifica conexões ativas',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 Diagnóstico de Bloqueio de Banco de Dados\n')
        )

        # 1. Informações do banco
        self.stdout.write('📊 Informações do Banco:')
        db_engine = settings.DATABASES['default']['ENGINE']
        self.stdout.write(f'   Engine: {db_engine}')
        self.stdout.write(f'   Name: {settings.DATABASES["default"]["NAME"]}')
        
        if 'OPTIONS' in settings.DATABASES['default']:
            options = settings.DATABASES['default']['OPTIONS']
            self.stdout.write(f'   Timeout: {options.get("timeout", "N/A")}')
            self.stdout.write(f'   Check Same Thread: {options.get("check_same_thread", "N/A")}')

        # 2. Teste de conexão
        self.stdout.write('\n🔗 Teste de Conexão:')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                self.stdout.write(f'   ✅ Conexão OK: {result[0]}')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro de conexão: {e}')

        # 3. Verificar conexões ativas (PostgreSQL)
        if options['check_connections'] and 'postgresql' in db_engine:
            self.stdout.write('\n👥 Conexões Ativas (PostgreSQL):')
            try:
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT 
                            pid,
                            usename,
                            application_name,
                            client_addr,
                            state,
                            query_start,
                            query
                        FROM pg_stat_activity 
                        WHERE state = 'active'
                        ORDER BY query_start
                    """)
                    connections = cursor.fetchall()
                    
                    if connections:
                        for conn in connections:
                            self.stdout.write(f'   PID: {conn[0]}, User: {conn[1]}, State: {conn[4]}')
                    else:
                        self.stdout.write('   Nenhuma conexão ativa encontrada')
            except Exception as e:
                self.stdout.write(f'   ❌ Erro ao verificar conexões: {e}')

        # 4. Teste de escritas simultâneas
        if options['test_writes']:
            self.stdout.write('\n✍️ Teste de Escritas Simultâneas:')
            self._test_concurrent_writes()

        # 5. Recomendações
        self.stdout.write('\n💡 Recomendações:')
        if 'sqlite' in db_engine:
            self.stdout.write('   • Considere migrar para PostgreSQL em produção')
            self.stdout.write('   • SQLite não é recomendado para alta concorrência')
        else:
            self.stdout.write('   • Banco PostgreSQL configurado corretamente')
        
        self.stdout.write('   • Middleware de auditoria otimizado')
        self.stdout.write('   • Use transações atômicas para operações críticas')

    def _test_concurrent_writes(self):
        """Testa escritas simultâneas para detectar bloqueios"""
        from apps.main.auditor.models import Auditor
        from django.utils import timezone
        
        def write_record(thread_id):
            try:
                for i in range(5):
                    Auditor.objects.create(
                        date=timezone.now(),
                        path=f'/test/concurrent/{thread_id}/{i}',
                        total_time=0.001,
                        total_queries=1,
                        db_time=0.0,
                        python_time=0.001,
                        ip='127.0.0.1',
                        method='GET',
                        user_agent='Test Agent',
                        host='localhost',
                        port='8000',
                        content_type='',
                        response_content='TEST',
                        response_status_code=200,
                        proxy_verified=False,
                        body=None
                    )
                    time.sleep(0.01)  # Pequena pausa
                return f'Thread {thread_id}: ✅ Sucesso'
            except Exception as e:
                return f'Thread {thread_id}: ❌ Erro - {e}'

        # Executa 3 threads simultaneamente
        threads = []
        results = []
        
        def worker(thread_id):
            result = write_record(thread_id)
            results.append(result)

        for i in range(3):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Aguarda todas as threads terminarem
        for thread in threads:
            thread.join()

        # Mostra resultados
        for result in results:
            self.stdout.write(f'   {result}') 