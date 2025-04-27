from celery import shared_task
import logging


logger = logging.getLogger(__name__)


@shared_task
def encerrar_leiloes_expirados():
    from .services import finish_auction
    from .models import Auction
    from django.utils.timezone import now

    expirados = Auction.objects.filter(end_time__lte=now())
    count = expirados.count()
    for leilao in expirados:
        try:
            if leilao.is_active():  # Usando o método is_active()
                finish_auction(leilao)
        except Exception as e:
            logger.error(f'Erro ao encerrar leilão {leilao.id}: {e}')
    logger.info(f'{count} leilões encerrados automaticamente.')
