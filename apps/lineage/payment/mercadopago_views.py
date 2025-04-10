from django.shortcuts import render, redirect
from django.conf import settings
import mercadopago
from .models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


def pagamento_sucesso(request):
    return HttpResponse("Pagamento aprovado com sucesso!")


def pagamento_erro(request):
    return HttpResponse("Pagamento cancelado ou falhou.")


@csrf_exempt
@require_POST
def notificacao_mercado_pago(request):
    import json
    body = json.loads(request.body)
    payment_id = body.get("data", {}).get("id")

    if payment_id:
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
        result = sdk.payment().get(payment_id)

        if result["status"] == 200:
            pagamento_info = result["response"]
            status = pagamento_info["status"]
            pagamento_id = pagamento_info["metadata"].get("pagamento_id")

            if pagamento_id:
                try:
                    pagamento = Pagamento.objects.get(id=pagamento_id)
                    pagamento.status = status.capitalize()
                    pagamento.save()

                    if status == "approved":
                        # Aqui você pode creditar as moedas na Wallet, etc
                        pass

                    return HttpResponse("Notificação processada", status=200)
                except Pagamento.DoesNotExist:
                    pass

    return HttpResponse("Erro ao processar notificação", status=400)
