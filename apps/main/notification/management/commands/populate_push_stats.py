from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.main.notification.models import PushNotificationLog, PushSubscription
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Popula dados de exemplo para estatísticas de push notifications'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5, help='Número de usuários para criar')
        parser.add_argument('--notifications', type=int, default=10, help='Número de notificações para criar')

    def handle(self, *args, **options):
        num_users = options['users']
        num_notifications = options['notifications']
        
        # Criar usuários de exemplo se não existirem
        users = []
        for i in range(num_users):
            username = f'testuser{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@example.com',
                    'is_staff': True,
                    'is_superuser': True
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Usuário criado: {username}')
        
        # Criar subscriptions de exemplo
        for user in users:
            PushSubscription.objects.get_or_create(
                user=user,
                endpoint=f'https://example.com/push/{user.id}',
                defaults={
                    'auth': f'auth_{user.id}',
                    'p256dh': f'p256dh_{user.id}'
                }
            )
        
        # Criar logs de notificações push de exemplo
        messages = [
            "Manutenção programada hoje às 22h",
            "Novo evento disponível! Participe agora",
            "Atualização do sistema concluída",
            "Promoção especial: 50% de desconto",
            "Servidor reiniciado com sucesso",
            "Novo conteúdo disponível",
            "Lembrete: Backup automático em 1 hora",
            "Sistema de chat temporariamente indisponível",
            "Nova funcionalidade liberada",
            "Correção de bugs aplicada"
        ]
        
        for i in range(num_notifications):
            # Data aleatória nos últimos 30 dias
            days_ago = random.randint(0, 30)
            created_at = timezone.now() - timedelta(days=days_ago)
            
            # Estatísticas realistas
            total_subscribers = random.randint(3, len(users))
            successful_sends = random.randint(total_subscribers - 2, total_subscribers)
            failed_sends = total_subscribers - successful_sends
            
            PushNotificationLog.objects.create(
                message=random.choice(messages),
                sent_by=random.choice(users),
                total_subscribers=total_subscribers,
                successful_sends=successful_sends,
                failed_sends=failed_sends,
                created_at=created_at
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Dados de exemplo criados: {len(users)} usuários, {num_notifications} notificações push'
            )
        ) 