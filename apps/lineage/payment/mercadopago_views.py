from django.shortcuts import render
from django.conf import settings
import mercadopago
from .models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from apps.lineage.wallet.signals import aplicar_transacao
from apps.lineage.wallet.models import Wallet
from django.db import transaction
import logging


logger = logging.getLogger(__name__)


def pagamento_sucesso(request):
    return render(request, 'mp/pagamento_sucesso.html')


def pagamento_erro(request):
    return render(request, 'mp/pagamento_erro.html')


@csrf_exempt
@require_POST
def notificacao_mercado_pago(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse("JSON inválido", status=400)

    tipo = request.GET.get("type")
    data_id = request.GET.get("data.id")

    if not tipo or not data_id:
        return HttpResponse("Parâmetros inválidos", status=400)

    # Salva o log da notificação
    WebhookLog.objects.create(
        tipo=tipo,
        data_id=data_id,
        payload=body
    )

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    if tipo == "payment":
        result = sdk.payment().get(data_id)

        if result["status"] == 200:
            pagamento_info = result["response"]
            status = pagamento_info["status"]
            pagamento_id = pagamento_info["metadata"].get("pagamento_id")

            if pagamento_id:
                try:
                    pagamento = Pagamento.objects.get(id=pagamento_id)

                    # Só processa se ainda não estiver aprovado
                    if status == "approved" and pagamento.status != "Approved":
                        with transaction.atomic():
                            wallet, _ = Wallet.objects.get_or_create(usuario=pagamento.usuario)
                            aplicar_transacao(
                                wallet=wallet,
                                tipo="ENTRADA",
                                valor=pagamento.valor,
                                descricao="Crédito via MercadoPago",
                                origem="MercadoPago",
                                destino=pagamento.usuario.username
                            )
                            pagamento.status = "Approved"
                            pagamento.save()

                    return HttpResponse("Notificação de pagamento processada", status=200)

                except Pagamento.DoesNotExist:
                    return HttpResponse("Pagamento não encontrado", status=404)
                except Exception as e:
                    logger.error(f"Erro ao aplicar transação: {e}")
                    return HttpResponse("Erro interno ao processar transação", status=500)

        return HttpResponse("Erro ao buscar pagamento", status=400)

    elif tipo == "merchant_order":
        result = sdk.merchant_order().get(data_id)

        if result["status"] == 200:
            order = result["response"]
            pagamentos = order.get("payments", [])
            aprovado = any(p["status"] == "approved" for p in pagamentos)

            if aprovado:
                external_reference = order.get("external_reference")
                if external_reference:
                    try:
                        pagamento = Pagamento.objects.get(id=external_reference)

                        if pagamento.status != "Approved":
                            pagamento.status = "Approved"
                            pagamento.save()

                        return HttpResponse("Notificação de merchant order processada", status=200)
                    except Pagamento.DoesNotExist:
                        return HttpResponse("Pagamento não encontrado pela referência", status=404)
                else:
                    return HttpResponse("Referência externa ausente", status=400)

            return HttpResponse("Ordem ainda não paga", status=200)

        return HttpResponse("Erro ao buscar merchant order", status=400)

    return HttpResponse("Tipo de notificação não suportado", status=400)
