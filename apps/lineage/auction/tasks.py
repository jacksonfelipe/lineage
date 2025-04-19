from celery import shared_task
from .models import Auction
from django.utils import timezone

@shared_task
def encerrar_leiloes_expirados():
    from .services import finish_auction
    expirados = Auction.objects.filter(end_time__lte=timezone.now(), is_active=True)
    for leilao in expirados:
        finish_auction(leilao)
