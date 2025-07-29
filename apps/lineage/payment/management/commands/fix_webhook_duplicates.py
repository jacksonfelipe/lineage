from django.core.management.base import BaseCommand
from django.db import connection
import uuid


class Command(BaseCommand):
    help = 'Corrige UUIDs duplicados no WebhookLog'

    def handle(self, *args, **options):
        self.stdout.write("🔍 Verificando UUIDs duplicados...")
        
        with connection.cursor() as cursor:
            # Encontrar UUIDs duplicados
            cursor.execute("""
                SELECT uuid, COUNT(*) as count
                FROM payment_webhooklog
                GROUP BY uuid
                HAVING COUNT(*) > 1
            """)
            
            duplicates = cursor.fetchall()
            
            if not duplicates:
                self.stdout.write(
                    self.style.SUCCESS("✅ Nenhum UUID duplicado encontrado!")
                )
                return
            
            self.stdout.write(
                self.style.WARNING(f"⚠️  Encontrados {len(duplicates)} UUIDs duplicados")
            )
            
            for duplicate_uuid, count in duplicates:
                self.stdout.write(f"   UUID: {duplicate_uuid} - {count} registros")
                
                # Pegar todos os registros com este UUID
                cursor.execute("""
                    SELECT id FROM payment_webhooklog
                    WHERE uuid = %s
                    ORDER BY id
                """, [duplicate_uuid])
                
                records = cursor.fetchall()
                
                # Manter o primeiro registro, atualizar os outros com novos UUIDs
                for i, (record_id,) in enumerate(records[1:], 1):
                    new_uuid = str(uuid.uuid4())
                    cursor.execute("""
                        UPDATE payment_webhooklog
                        SET uuid = %s
                        WHERE id = %s
                    """, [new_uuid, record_id])
                    
                    self.stdout.write(f"      Registro {record_id}: UUID atualizado para {new_uuid}")
        
        self.stdout.write(
            self.style.SUCCESS("✅ Correção de UUIDs duplicados concluída!")
        )