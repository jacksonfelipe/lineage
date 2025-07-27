import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.lineage.server.database import LineageDB

User = get_user_model()


class Command(BaseCommand):
    help = 'Verifica quais emails do L2 já existem no PDL'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 VERIFICANDO CONFLITOS DE EMAIL')
        )
        
        # Verifica conexão com o banco L2
        if not LineageDB().is_connected():
            self.stderr.write(
                self.style.ERROR('❌ Não foi possível conectar ao banco do L2')
            )
            return

        try:
            # Busca emails do L2
            sql = """
                SELECT login, l2email as email
                FROM accounts 
                WHERE l2email IS NOT NULL 
                AND l2email != '' 
                AND l2email != 'NULL' 
                AND LENGTH(TRIM(l2email)) > 0
                ORDER BY l2email ASC
            """
            
            l2_accounts = LineageDB().select(sql)
            
            if not l2_accounts:
                self.stdout.write('⚠️  Nenhuma conta com email encontrada no L2')
                return
            
            self.stdout.write(f'📧 Verificando {len(l2_accounts)} emails do L2...')
            
            # Verifica conflitos
            conflicts = []
            unique_emails = set()
            
            for account in l2_accounts:
                email = account['email']
                
                # Verifica se já existe no PDL
                if User.objects.filter(email=email).exists():
                    conflicts.append({
                        'login': account['login'],
                        'email': email,
                        'type': 'existe_no_pdl'
                    })
                
                # Verifica duplicatas no próprio L2
                if email in unique_emails:
                    conflicts.append({
                        'login': account['login'],
                        'email': email,
                        'type': 'duplicado_no_l2'
                    })
                else:
                    unique_emails.add(email)
            
            # Relatório
            self.stdout.write(f'\n📊 RELATÓRIO DE CONFLITOS:')
            self.stdout.write(f'Total de emails únicos no L2: {len(unique_emails)}')
            self.stdout.write(f'Conflitos encontrados: {len(conflicts)}')
            
            if conflicts:
                self.stdout.write('\n⚠️  CONFLITOS DETECTADOS:')
                for conflict in conflicts:
                    if conflict['type'] == 'existe_no_pdl':
                        self.stdout.write(f'  - {conflict["login"]} → {conflict["email"]} (já existe no PDL)')
                    else:
                        self.stdout.write(f'  - {conflict["login"]} → {conflict["email"]} (duplicado no L2)')
            else:
                self.stdout.write('\n✅ Nenhum conflito encontrado!')
            
            # Estatísticas por tipo
            pdl_conflicts = [c for c in conflicts if c['type'] == 'existe_no_pdl']
            l2_duplicates = [c for c in conflicts if c['type'] == 'duplicado_no_l2']
            
            self.stdout.write(f'\n📈 DETALHAMENTO:')
            self.stdout.write(f'  - Já existem no PDL: {len(pdl_conflicts)}')
            self.stdout.write(f'  - Duplicados no L2: {len(l2_duplicates)}')
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro durante verificação: {e}')
            ) 