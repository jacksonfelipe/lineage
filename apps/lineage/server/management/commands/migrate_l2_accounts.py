import os
import secrets
import string
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class

User = get_user_model()


class Command(BaseCommand):
    help = 'Migra contas do banco do L2 para o PDL seguindo regras específicas'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Executa em modo de teste sem criar usuários',
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='L2_',
            help='Prefixo para emails duplicados (padrão: L2_)',
        )
        parser.add_argument(
            '--password-length',
            type=int,
            default=64,
            help='Comprimento da senha aleatória (padrão: 64)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Tamanho do lote para processamento (padrão: 100)',
        )

    def generate_random_password(self, length=64):
        """Gera uma senha aleatória de 64 bits"""
        alphabet = string.ascii_letters + string.digits + string.punctuation
        # Remove caracteres que podem causar problemas em alguns sistemas
        alphabet = alphabet.replace('"', '').replace("'", '').replace('\\', '').replace('`', '')
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_random_prefix(self, length=6):
        """Gera um prefixo aleatório para emails duplicados"""
        alphabet = string.ascii_uppercase + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def validate_and_fix_username(self, login):
        """Valida e corrige username se necessário"""
        if not login:
            return None
            
        # Remove caracteres inválidos e espaços
        login = ''.join(c for c in login if c.isalnum() or c in '_-')
        
        # Trunca se for muito longo (máximo 16 caracteres)
        if len(login) > 16:
            login = login[:16]
            
        # Garante que não está vazio
        if not login:
            return None
            
        return login

    def get_l2_accounts(self):
        """Busca contas do L2 com email válido"""
        try:
            LineageAccount = get_query_class("LineageAccount")
            
            # Busca todas as contas com email válido na coluna l2email
            sql = """
                SELECT login, 
                       l2email as email,
                       accessLevel, 
                       created_time
                FROM accounts 
                WHERE l2email IS NOT NULL 
                AND l2email != '' 
                AND l2email != 'NULL' 
                AND LENGTH(TRIM(l2email)) > 0
                ORDER BY created_time ASC
            """
            
            accounts = LineageDB().select(sql)
            return accounts
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro ao buscar contas do L2: {e}')
            )
            return []

    def check_email_exists(self, email):
        """Verifica se o email já existe no PDL"""
        return User.objects.filter(email=email).exists()

    def create_pdl_user(self, login, email, password, access_level, created_time):
        """Cria usuário no PDL"""
        try:
            # Verifica se o username já existe
            if User.objects.filter(username=login).exists():
                self.stdout.write(
                    self.style.WARNING(f'Username {login} já existe no PDL - pulando')
                )
                return False, None

            # Cria o usuário
            user = User.objects.create_user(
                username=login,
                email=email,
                password=password,
                is_active=True,
                is_email_verified=False,  # Não verificado por padrão
                is_2fa_enabled=False,     # 2FA desabilitado por padrão
            )
            
            # Define o nível de acesso baseado no access_level do L2
            if access_level is not None and int(access_level) > 0:
                user.is_staff = True
                if int(access_level) >= 100:  # GM ou superior
                    user.is_superuser = True
            
            user.save()
            
            return True, user
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro ao criar usuário {login}: {e}')
            )
            return False, None

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        prefix = options['prefix']
        password_length = options['password_length']
        batch_size = options['batch_size']

        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando migração de contas L2 → PDL')
        )
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('⚠️  MODO DE TESTE - Nenhum usuário será criado')
            )

        # Verifica conexão com o banco L2
        if not LineageDB().is_connected():
            self.stderr.write(
                self.style.ERROR('❌ Não foi possível conectar ao banco do L2')
            )
            return

        # Busca contas do L2
        self.stdout.write('📋 Buscando contas do L2...')
        l2_accounts = self.get_l2_accounts()
        
        if not l2_accounts:
            self.stdout.write(
                self.style.WARNING('⚠️  Nenhuma conta encontrada no L2')
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'✅ Encontradas {len(l2_accounts)} contas no L2')
        )

        # Estatísticas
        stats = {
            'total': len(l2_accounts),
            'created': 0,
            'skipped': 0,
            'errors': 0,
            'email_conflicts': 0,
            'l2_duplicates': 0,
        }

        # Processa emails duplicados dentro da lista L2
        email_count = {}
        processed_accounts = []
        
        for account in l2_accounts:
            login = account.get('login')
            email = account.get('email')
            access_level = account.get('accessLevel', 0)
            created_time = account.get('created_time')
            
            if not login or not email:
                stats['skipped'] += 1
                continue

            # Valida e corrige username
            original_login = login
            login = self.validate_and_fix_username(login)
            if not login:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Username inválido: {original_login} - pulando')
                )
                stats['skipped'] += 1
                continue

            # Conta ocorrências de cada email
            if email in email_count:
                email_count[email] += 1
                # Gera prefixo aleatório para duplicatas
                random_prefix = self.generate_random_prefix()
                email = f"{random_prefix}_{email}"
                stats['l2_duplicates'] += 1
                self.stdout.write(
                    self.style.WARNING(f'🔄 Email duplicado no L2: {login} → {email}')
                )
            else:
                email_count[email] = 1

            # Adiciona à lista processada
            processed_accounts.append({
                'login': login,
                'email': email,
                'access_level': access_level,
                'created_time': created_time
            })

        # Processa as contas em lotes
        self.stdout.write(f'🔄 Processando {len(processed_accounts)} contas em lotes de {batch_size}...')
        
        for i in range(0, len(processed_accounts), batch_size):
            batch = processed_accounts[i:i + batch_size]
            
            self.stdout.write(f'📦 Processando lote {i//batch_size + 1}/{(len(processed_accounts) + batch_size - 1)//batch_size} ({len(batch)} contas)')
            
            for account in batch:
                login = account.get('login')
                email = account.get('email')
                access_level = account.get('access_level', 0)
                created_time = account.get('created_time')

                # Verifica se o username já existe no PDL
                if User.objects.filter(username=login).exists():
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Username {login} já existe no PDL - pulando')
                    )
                    stats['skipped'] += 1
                    continue

                # Verifica se o email já existe no PDL
                original_email = email
                if self.check_email_exists(email):
                    # Adiciona prefixo para emails duplicados
                    email = f"{prefix}{email}"
                    stats['email_conflicts'] += 1
                    
                    if self.check_email_exists(email):
                        # Se ainda existe com prefixo, pula
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Email duplicado mesmo com prefixo: {email}')
                        )
                        stats['skipped'] += 1
                        continue

                # Gera senha aleatória
                password = self.generate_random_password(password_length)
                
                if dry_run:
                    self.stdout.write(
                        f'🔍 [TESTE] Criaria: {login} → {email} (access: {access_level})'
                    )
                    stats['created'] += 1
                else:
                    # Cria o usuário no PDL com transação
                    with transaction.atomic():
                        success, user = self.create_pdl_user(
                            login, email, password, access_level, created_time
                        )
                    
                    if success:
                        self.stdout.write(
                            self.style.SUCCESS(f'✅ Criado: {login} → {email}')
                        )
                        stats['created'] += 1
                        
                        # Log da senha (apenas para administradores)
                        if access_level and int(access_level) > 0:
                            self.stdout.write(
                                f'🔑 Senha para {login}: {password}'
                            )
                    else:
                        self.stdout.write(
                            self.style.ERROR(f'❌ Erro ao criar: {login} → {email}')
                        )
                        stats['errors'] += 1

        # Relatório final
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 RELATÓRIO DE MIGRAÇÃO'))
        self.stdout.write('='*60)
        self.stdout.write(f'Total de contas processadas: {stats["total"]}')
        self.stdout.write(f'Usuários criados: {stats["created"]}')
        self.stdout.write(f'Pulados: {stats["skipped"]}')
        self.stdout.write(f'Erros: {stats["errors"]}')
        self.stdout.write(f'Emails duplicados no L2: {stats["l2_duplicates"]}')
        self.stdout.write(f'Conflitos com PDL resolvidos: {stats["email_conflicts"]}')
        
        if dry_run:
            self.stdout.write('\n⚠️  MODO DE TESTE - Execute sem --dry-run para criar os usuários')
        else:
            self.stdout.write('\n✅ Migração concluída!')
            self.stdout.write('\n📝 PRÓXIMOS PASSOS:')
            self.stdout.write('1. Os usuários precisam definir suas próprias senhas')
            self.stdout.write('2. Eles devem usar a senha do L2 para confirmar a veracidade da conta')
            self.stdout.write('3. As contas não estão vinculadas (conforme solicitado)')
            self.stdout.write('4. Considere enviar emails informativos aos usuários') 