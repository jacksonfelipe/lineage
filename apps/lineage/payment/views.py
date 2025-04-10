from django.shortcuts import render, redirect
from django.conf import settings
import mercadopago
from .models import *
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


@login_required
def purchase(request):
    """
    Formulário onde o usuário informa o valor a pagar e escolhe o método (ex: MercadoPago)
    """
    if request.method == 'POST':
        valor = float(request.POST.get('valor'))
        metodo = request.POST.get('metodo')

        # Aqui você pode adicionar validações extras

        return redirect('payment:confirmar_pagamento', valor=valor, metodo=metodo)

    return render(request, "payment/purchase.html")  # Deve ter <form method="post"> com campos valor e metodo


@login_required
def confirmar_pagamento(request, valor, metodo):
    usuario = request.user
    moedas = float(valor)

    pedido = PedidoPagamento.objects.create(
        usuario=usuario,
        valor_pago=valor,
        moedas_geradas=moedas,
        metodo=metodo
    )

    pagamento = Pagamento.objects.create(
        usuario=usuario,
        valor=valor,
        status="Pendente",
        pedido_pagamento=pedido
    )

    if metodo == "MercadoPago":
        sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

        preference_data = {
            "items": [
                {
                    "title": "Moedas para o jogo",
                    "quantity": 1,
                    "currency_id": "BRL",
                    "unit_price": float(valor),
                }
            ],
            "back_urls": {
                "success": settings.MERCADO_PAGO_SUCCESS_URL,
                "failure": settings.MERCADO_PAGO_FAILURE_URL,
            },
            "auto_return": "approved",
            "metadata": {
                "pagamento_id": pagamento.id
            }
        }

        preference_response = sdk.preference().create(preference_data)

        if preference_response.get("status") != 201:
            erro = preference_response.get("response", {}).get("message", "Erro desconhecido")
            return HttpResponse(f"Erro ao criar preferência de pagamento: {erro}", status=500)

        preference = preference_response.get("response", {})

        if "id" not in preference or "init_point" not in preference:
            return HttpResponse("Resposta inválida do Mercado Pago.", status=500)

        pagamento.transaction_code = preference["id"]
        pagamento.save()

        return redirect(preference["init_point"])

    return HttpResponse("Método de pagamento não suportado.", status=400)


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
