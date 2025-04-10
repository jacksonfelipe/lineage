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
import hmac
import hashlib
import urllib.parse


logger = logging.getLogger(__name__)


def validar_assinatura_hmac(request):
    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    if not x_signature or not x_request_id:
        logger.warning("Cabeçalhos ausentes para verificação HMAC.")
        return False

    query_string = urllib.parse.urlparse(request.get_raw_uri()).query
    query_params = urllib.parse.parse_qs(query_string)
    data_id = query_params.get("data.id", [""])[0]

    if not data_id:
        logger.warning("Query param data.id ausente.")
        return False

    parts = x_signature.split(",")
    ts = None
    v1 = None

    for part in parts:
        key_value = part.strip().split("=", 1)
        if len(key_value) == 2:
            key, value = key_value
            if key == "ts":
                ts = value
            elif key == "v1":
                v1 = value

    if not all([ts, v1]):
        logger.warning("Partes da assinatura ausentes.")
        return False

    # Monta o manifesto como especificado na doc do Mercado Pago
    manifest = f"id:{data_id};request-id:{x_request_id};ts:{ts};"

    # Obtém a chave secreta do settings
    secret = settings.MERCADO_PAGO_WEBHOOK_SECRET

    hmac_obj = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256)
    expected_signature = hmac_obj.hexdigest()

    if not hmac.compare_digest(expected_signature, v1):
        logger.warning("Assinatura HMAC inválida.")
        return False

    return True


def pagamento_sucesso(request):
    return render(request, 'mp/pagamento_sucesso.html')


def pagamento_erro(request):
    return render(request, 'mp/pagamento_erro.html')


@csrf_exempt
@require_POST
def notificacao_mercado_pago(request):
    if not validar_assinatura_hmac(request):
        return HttpResponse("Assinatura inválida", status=403)

    try:
        body = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return HttpResponse("JSON inválido", status=400)

    tipo = body.get("type")
    data = body.get("data", {})

    # Corrigir o data_id dependendo do tipo
    if tipo == "payment":
        data_id = data.get("id")
    elif tipo in ["merchant_order", "topic_merchant_order_wh"]:
        data_id = body.get("id")  # vem fora do campo data
    else:
        data_id = data.get("id")  # fallback genérico

    if not tipo or not data_id:
        return HttpResponse("Parâmetros inválidos", status=400)

    WebhookLog.objects.create(
        tipo=tipo,
        data_id=str(data_id),
        payload=body
    )

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    if tipo == "payment":
        result = sdk.payment().get(data_id)

        if result["status"] == 200:
            pagamento_info = result["response"]
            status = pagamento_info["status"]
            pagamento_id = pagamento_info.get("metadata", {}).get("pagamento_id")

            if pagamento_id:
                try:
                    pagamento = Pagamento.objects.get(id=pagamento_id)

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

    elif tipo in ["merchant_order", "topic_merchant_order_wh"]:
        result = sdk.merchant_order().get(data_id)

        if result["status"] == 200:
            order = result["response"]
            pagamentos = order.get("payments", [])
            aprovado = any(p.get("status") == "approved" for p in pagamentos)

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
