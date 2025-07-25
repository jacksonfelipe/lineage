from django.core.management.base import BaseCommand
from django.conf import settings
from apps.main.notification.models import PushSubscription
from pywebpush import webpush, WebPushException
import json

class Command(BaseCommand):
    help = 'Envia uma notificação push para todos os inscritos.'

    def add_arguments(self, parser):
        parser.add_argument('--message', type=str, default='Olá! Esta é uma notificação de teste do seu PWA.', help='Mensagem a ser enviada')

    def handle(self, *args, **options):
        message = options['message']
        total = 0
        for sub in PushSubscription.objects.all():
            subscription_info = {
                "endpoint": sub.endpoint,
                "keys": {
                    "p256dh": getattr(sub, 'p256dh', ''),
                    "auth": sub.auth,
                }
            }
            try:
                webpush(
                    subscription_info=subscription_info,
                    data=json.dumps({"body": message}),
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": "mailto:seu@email.com"}
                )
                self.stdout.write(self.style.SUCCESS(f"Notificação enviada para {sub.user} ({sub.endpoint[:30]}...)"))
                total += 1
            except WebPushException as ex:
                self.stdout.write(self.style.ERROR(f"Erro ao enviar para {sub.user}: {repr(ex)}"))
        self.stdout.write(self.style.SUCCESS(f"Total de notificações enviadas: {total}")) 