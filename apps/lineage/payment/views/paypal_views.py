import logging
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render, redirect
from apps.lineage.wallet.models import Wallet
from apps.lineage.wallet.signals import aplicar_transacao
from utils.notifications import send_notification
from ..models import Pagamento, WebhookLog


logger = logging.getLogger(__name__)


@csrf_exempt
def paypal_webhook(request):
    if request.method != 'POST':
        return HttpResponse(status=405)

    data = request.POST.dict()
    logger.info(f"Webhook do PayPal recebido: {data}")

    WebhookLog.objects.create(
        tipo=data.get("payment_status", "unknown"),
        data_id=data.get("txn_id", "no-txn"),
        payload=data
    )

    payment_status = data.get("payment_status")
    pagamento_id = data.get("custom")
    valor = data.get("mc_gross")
    valor = 0.0

    if payment_status == "Completed" and pagamento_id:
        try:
            pagamento = Pagamento.objects.get(id=pagamento_id)

            if pagamento.status == "pending":
                wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                aplicar_transacao(
                    wallet=wallet,
                    tipo="ENTRADA",
                    valor=float(valor),
                    descricao="Crédito via PayPal",
                    origem="PayPal",
                    destino=pagamento.usuario.username
                )
                pagamento.status = "paid"
                pagamento.save()

                pedido = pagamento.pedido_pagamento
                pedido.status = "CONCLUÍDO"
                pedido.save()

                send_notification(
                    user=None,
                    notification_type='staff',
                    message=f"Pagamento aprovado via PayPal para {pagamento.usuario.username} no valor de R$ {valor}.",
                    created_by=pagamento.usuario
                )
        except Pagamento.DoesNotExist:
            logger.error(f"Pagamento ID {pagamento_id} não encontrado.")
            return HttpResponse(status=404)

    return HttpResponse("OK", status=200)


def paypal_pagamento_sucesso(request):
    pagamento_id = request.GET.get("pagamento_id")

    if not pagamento_id:
        return redirect("payment:paypal_pagamento_erro")

    try:
        pagamento = Pagamento.objects.get(id=pagamento_id)

        if pagamento.status != "paid":
            wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
            aplicar_transacao(
                wallet=wallet,
                tipo="ENTRADA",
                valor=pagamento.valor,
                descricao="Crédito via PayPal (fallback)",
                origem="PayPal",
                destino=pagamento.usuario.username
            )
            pagamento.status = "paid"
            pagamento.save()

            pedido = pagamento.pedido_pagamento
            pedido.status = "CONCLUÍDO"
            pedido.save()

            WebhookLog.objects.create(
                tipo="paypal_fallback",
                data_id=str(pagamento.id),
                payload={"fallback": True}
            )

        return render(request, "paypal/pagamento_sucesso.html")

    except Exception as e:
        logger.exception("Erro ao processar sucesso do PayPal.")
        return redirect("payment:paypal_pagamento_erro")


def paypal_pagamento_erro(request):
    return render(request, "paypal/pagamento_erro.html")
