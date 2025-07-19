from django.core.management.base import BaseCommand
from django.conf import settings
import logging

class Command(BaseCommand):
    help = 'Testa se o servidor inicia sem erros de configuração'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔧 Teste de Configuração do Servidor\n')
        )

        # 1. Testa configuração de logging
        self.stdout.write('📋 Verificando configuração de logging...')
        try:
            # Verifica se LOGGING está configurado
            if hasattr(settings, 'LOGGING'):
                self.stdout.write('   ✅ LOGGING configurado')
                
                # Verifica handlers
                handlers = settings.LOGGING.get('handlers', {})
                self.stdout.write(f'   📊 Handlers disponíveis: {list(handlers.keys())}')
                
                # Verifica loggers
                loggers = settings.LOGGING.get('loggers', {})
                self.stdout.write(f'   📊 Loggers configurados: {list(loggers.keys())}')
                
                # Verifica se os handlers referenciados existem
                for logger_name, logger_config in loggers.items():
                    logger_handlers = logger_config.get('handlers', [])
                    for handler in logger_handlers:
                        if handler not in handlers:
                            self.stdout.write(
                                self.style.WARNING(f'   ⚠️ Logger {logger_name} referencia handler inexistente: {handler}')
                            )
                        else:
                            self.stdout.write(f'   ✅ Logger {logger_name} -> handler {handler} OK')
            else:
                self.stdout.write('   ❌ LOGGING não configurado')
                
        except Exception as e:
            self.stdout.write(f'   ❌ Erro na configuração de logging: {e}')

        # 2. Testa configuração de banco
        self.stdout.write('\n🗄️ Verificando configuração de banco...')
        try:
            databases = getattr(settings, 'DATABASES', {})
            if 'default' in databases:
                db_config = databases['default']
                engine = db_config.get('ENGINE', 'N/A')
                name = db_config.get('NAME', 'N/A')
                self.stdout.write(f'   ✅ Banco configurado: {engine}')
                self.stdout.write(f'   📊 Nome do banco: {name}')
            else:
                self.stdout.write('   ❌ Configuração de banco não encontrada')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro na configuração de banco: {e}')

        # 3. Testa configuração de autenticação
        self.stdout.write('\n🔐 Verificando configuração de autenticação...')
        try:
            auth_backends = getattr(settings, 'AUTHENTICATION_BACKENDS', [])
            self.stdout.write(f'   📊 Backends configurados: {len(auth_backends)}')
            for i, backend in enumerate(auth_backends, 1):
                self.stdout.write(f'   {i}. {backend}')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro na configuração de autenticação: {e}')

        # 4. Testa importação de módulos críticos
        self.stdout.write('\n📦 Verificando importações críticas...')
        try:
            from django.contrib.auth import authenticate
            self.stdout.write('   ✅ django.contrib.auth OK')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro em django.contrib.auth: {e}')

        try:
            from core.backends import LicenseBackend
            self.stdout.write('   ✅ core.backends.LicenseBackend OK')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro em core.backends: {e}')

        try:
            from utils.license_manager import check_license_status
            self.stdout.write('   ✅ utils.license_manager OK')
        except Exception as e:
            self.stdout.write(f'   ❌ Erro em utils.license_manager: {e}')

        # 5. Resumo
        self.stdout.write('\n🎯 Resumo:')
        self.stdout.write('   • Se todos os itens estão ✅, o servidor deve iniciar normalmente')
        self.stdout.write('   • Se há ❌, corrija os problemas antes de iniciar o servidor')
        self.stdout.write('   • Use "python manage.py runserver" para testar o servidor') 