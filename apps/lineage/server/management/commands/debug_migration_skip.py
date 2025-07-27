import os
from django.core.management.base import BaseCommand
from apps.lineage.server.database import LineageDB
from utils.dynamic_import import get_query_class


class Command(BaseCommand):
    help = 'Investiga por que contas estão sendo puladas na migração'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🔍 INVESTIGANDO CONTAS PULADAS')
        )
        
        # Verifica conexão com o banco L2
        if not LineageDB().is_connected():
            self.stderr.write(
                self.style.ERROR('❌ Não foi possível conectar ao banco do L2')
            )
            return

        try:
            # 1. Verificar contas com email em cada coluna
            sql_email_columns = """
                SELECT 
                    COUNT(*) as total,
                    SUM(CASE WHEN email IS NOT NULL AND email != '' AND email != 'NULL' THEN 1 ELSE 0 END) as email_count,
                    SUM(CASE WHEN l2email IS NOT NULL AND l2email != '' AND l2email != 'NULL' THEN 1 ELSE 0 END) as l2email_count,
                    SUM(CASE WHEN e_mail IS NOT NULL AND e_mail != '' AND e_mail != 'NULL' THEN 1 ELSE 0 END) as e_mail_count
                FROM accounts
            """
            email_result = LineageDB().select(sql_email_columns)
            if email_result:
                data = email_result[0]
                self.stdout.write(f'\n📧 Contas por coluna de email:')
                self.stdout.write(f'  - Total: {data["total"]}')
                self.stdout.write(f'  - Coluna "email": {data["email_count"]}')
                self.stdout.write(f'  - Coluna "l2email": {data["l2email_count"]}')
                self.stdout.write(f'  - Coluna "e_mail": {data["e_mail_count"]}')
            
            # 2. Verificar contas com pelo menos um email válido
            sql_any_email = """
                SELECT COUNT(*) as total
                FROM accounts 
                WHERE (email IS NOT NULL AND email != '' AND email != 'NULL')
                   OR (l2email IS NOT NULL AND l2email != '' AND l2email != 'NULL')
                   OR (e_mail IS NOT NULL AND e_mail != '' AND e_mail != 'NULL')
            """
            any_email_result = LineageDB().select(sql_any_email)
            any_email_count = any_email_result[0]['total'] if any_email_result else 0
            self.stdout.write(f'\n✅ Contas com pelo menos um email válido: {any_email_count}')
            
            # 3. Verificar contas sem nenhum email válido
            sql_no_email = """
                SELECT COUNT(*) as total
                FROM accounts 
                WHERE (email IS NULL OR email = '' OR email = 'NULL')
                   AND (l2email IS NULL OR l2email = '' OR l2email = 'NULL')
                   AND (e_mail IS NULL OR e_mail = '' OR e_mail = 'NULL')
            """
            no_email_result = LineageDB().select(sql_no_email)
            no_email_count = no_email_result[0]['total'] if no_email_result else 0
            self.stdout.write(f'❌ Contas sem nenhum email válido: {no_email_count}')
            
            # 4. Amostra de contas com email em l2email
            sql_l2email_sample = """
                SELECT login, l2email, accessLevel
                FROM accounts 
                WHERE l2email IS NOT NULL 
                AND l2email != '' 
                AND l2email != 'NULL'
                AND (email IS NULL OR email = '' OR email = 'NULL')
                LIMIT 10
            """
            l2email_sample = LineageDB().select(sql_l2email_sample)
            
            self.stdout.write('\n📋 Amostra de contas com email apenas em l2email:')
            for account in l2email_sample:
                self.stdout.write(f'  - {account["login"]} → {account["l2email"]} (access: {account["accessLevel"]})')
            
            # 5. Amostra de contas com email em e_mail
            sql_e_mail_sample = """
                SELECT login, e_mail, accessLevel
                FROM accounts 
                WHERE e_mail IS NOT NULL 
                AND e_mail != '' 
                AND e_mail != 'NULL'
                AND (email IS NULL OR email = '' OR email = 'NULL')
                AND (l2email IS NULL OR l2email = '' OR l2email = 'NULL')
                LIMIT 10
            """
            e_mail_sample = LineageDB().select(sql_e_mail_sample)
            
            self.stdout.write('\n📋 Amostra de contas com email apenas em e_mail:')
            for account in e_mail_sample:
                self.stdout.write(f'  - {account["login"]} → {account["e_mail"]} (access: {account["accessLevel"]})')
            
            # 6. Verificar se há contas com email duplicado
            sql_duplicate_check = """
                SELECT email, COUNT(*) as count
                FROM (
                    SELECT COALESCE(email, l2email, e_mail) as email
                    FROM accounts 
                    WHERE (email IS NOT NULL AND email != '' AND email != 'NULL')
                       OR (l2email IS NOT NULL AND l2email != '' AND l2email != 'NULL')
                       OR (e_mail IS NOT NULL AND e_mail != '' AND e_mail != 'NULL')
                ) as emails
                WHERE email IS NOT NULL
                GROUP BY email
                HAVING COUNT(*) > 1
                LIMIT 10
            """
            duplicate_result = LineageDB().select(sql_duplicate_check)
            
            if duplicate_result:
                self.stdout.write('\n⚠️  Emails duplicados encontrados:')
                for dup in duplicate_result:
                    self.stdout.write(f'  - {dup["email"]}: {dup["count"]} contas')
            else:
                self.stdout.write('\n✅ Nenhum email duplicado encontrado')
            
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Erro durante investigação: {e}')
            ) 