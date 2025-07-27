import os
from django.core.management.base import BaseCommand
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class


class Command(BaseCommand):
    help = 'Diagnóstico das contas do L2 para debug da migração'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 DIAGNÓSTICO DAS CONTAS L2')
        )
        
        # Verifica conexão com o banco L2
        if not LineageDB().is_connected():
            self.stderr.write(
                self.style.ERROR('❌ Não foi possível conectar ao banco do L2')
            )
            return

        try:
            # 1. Total de contas
            sql_total = "SELECT COUNT(*) as total FROM accounts"
            total_result = LineageDB().select(sql_total)
            total_accounts = total_result[0]['total'] if total_result else 0
            
            self.stdout.write(f'📊 Total de contas no L2: {total_accounts}')
            
            # 2. Contas com email
            sql_with_email = """
                SELECT COUNT(*) as total 
                FROM accounts 
                WHERE email IS NOT NULL 
                AND email != '' 
                AND email != 'NULL'
            """
            email_result = LineageDB().select(sql_with_email)
            accounts_with_email = email_result[0]['total'] if email_result else 0
            
            self.stdout.write(f'📧 Contas com email válido: {accounts_with_email}')
            
            # 3. Contas sem email
            sql_no_email = """
                SELECT COUNT(*) as total 
                FROM accounts 
                WHERE email IS NULL 
                OR email = '' 
                OR email = 'NULL'
            """
            no_email_result = LineageDB().select(sql_no_email)
            accounts_no_email = no_email_result[0]['total'] if no_email_result else 0
            
            self.stdout.write(f'❌ Contas sem email válido: {accounts_no_email}')
            
            # 4. Amostra de contas com email
            sql_sample = """
                SELECT login, email, accessLevel, created_time
                FROM accounts 
                WHERE email IS NOT NULL 
                AND email != '' 
                AND email != 'NULL'
                ORDER BY created_time ASC
                LIMIT 10
            """
            sample_accounts = LineageDB().select(sql_sample)
            
            self.stdout.write('\n📋 Amostra de contas com email:')
            for account in sample_accounts:
                self.stdout.write(f'  - {account["login"]} → {account["email"]} (access: {account["accessLevel"]})')
            
            # 5. Amostra de contas sem email
            sql_sample_no_email = """
                SELECT login, email, accessLevel, created_time
                FROM accounts 
                WHERE email IS NULL 
                OR email = '' 
                OR email = 'NULL'
                ORDER BY created_time ASC
                LIMIT 10
            """
            sample_no_email = LineageDB().select(sql_sample_no_email)
            
            self.stdout.write('\n❌ Amostra de contas sem email:')
            for account in sample_no_email:
                email_value = account["email"] if account["email"] else "NULL"
                self.stdout.write(f'  - {account["login"]} → {email_value} (access: {account["accessLevel"]})')
            
            # 6. Verificar nomes das colunas
            self.stdout.write('\n🔍 Verificando estrutura da tabela...')
            columns = LineageDB().get_table_columns('accounts')
            self.stdout.write(f'Colunas da tabela accounts: {", ".join(columns)}')
            
            # 7. Verificar se há diferença entre accessLevel e access_level
            sql_check_access = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN accessLevel IS NOT NULL THEN 1 ELSE 0 END) as with_accessLevel,
                    SUM(CASE WHEN access_level IS NOT NULL THEN 1 ELSE 0 END) as with_access_level
                FROM accounts
            """
            access_result = LineageDB().select(sql_check_access)
            if access_result:
                access_data = access_result[0]
                self.stdout.write(f'\n🔐 Verificação de access level:')
                self.stdout.write(f'  - Total: {access_data["total"]}')
                self.stdout.write(f'  - Com accessLevel: {access_data["with_accessLevel"]}')
                self.stdout.write(f'  - Com access_level: {access_data["with_access_level"]}')
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro durante diagnóstico: {e}')
            ) 