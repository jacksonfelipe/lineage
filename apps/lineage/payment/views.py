from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
import mercadopago
from .models import *
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from django.utils.timezone import now
from django.contrib import messages
from django.db import transaction


@login_required
def criar_ou_reaproveitar_pedido(request):
    if request.method == 'POST':
        try:
            valor = float(request.POST.get('valor'))
            if valor <= 0:
                return HttpResponse("Valor inválido", status=400)
        except (TypeError, ValueError):
            return HttpResponse("Valor inválido", status=400)

        metodo = request.POST.get('metodo')
        if metodo not in ["MercadoPago"]:  # Expanda conforme necessário
            return HttpResponse("Método de pagamento inválido", status=400)

        usuario = request.user
        duas_horas_atras = now() - timedelta(hours=2)

        with transaction.atomic():
            # Lock em todos os pedidos pendentes parecidos do usuário (para evitar criação duplicada)
            pedidos_similares = (
                PedidoPagamento.objects
                .select_for_update()
                .filter(
                    usuario=usuario,
                    valor_pago=valor,
                    metodo=metodo,
                    status='PENDENTE',
                    data_criacao__gte=duas_horas_atras
                )
            )

            pedido_existente = pedidos_similares.first()
            if pedido_existente:
                return redirect('payment:detalhes_pedido', pedido_id=pedido_existente.id)

            novo_pedido = PedidoPagamento.objects.create(
                usuario=usuario,
                valor_pago=valor,
                moedas_geradas=valor,
                metodo=metodo,
                status='PENDENTE'
            )
            return redirect('payment:detalhes_pedido', pedido_id=novo_pedido.id)

    return render(request, "payment/purchase.html")


@login_required
def confirmar_pagamento(request, pedido_id):
    try:
        with transaction.atomic():
            pedido = PedidoPagamento.objects.select_for_update().get(id=pedido_id, usuario=request.user)

            if pedido.status != 'PENDENTE':
                return HttpResponse("Pedido já processado ou inválido.")

            # Verifica se já existe um pagamento iniciado para esse pedido
            pagamento = Pagamento.objects.filter(pedido_pagamento=pedido).first()
            if pagamento:
                if pedido.metodo == "MercadoPago" and pagamento.transaction_code:
                    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                    preference_response = sdk.preference().get(pagamento.transaction_code)

                    if preference_response.get("status") != 200:
                        return HttpResponse("Erro ao recuperar preferência de pagamento", status=500)

                    preference = preference_response.get("response", {})
                    return redirect(preference["init_point"])

                return HttpResponse("Já existe um pagamento iniciado para este pedido.", status=400)

            # Cria novo pagamento
            pagamento = Pagamento.objects.create(
                usuario=request.user,
                valor=pedido.valor_pago,
                status="Pendente",
                pedido_pagamento=pedido
            )

            if pedido.metodo == "MercadoPago":
                sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
                preference_data = {
                    "items": [{
                        "title": "Moedas para o jogo",
                        "quantity": 1,
                        "currency_id": "BRL",
                        "unit_price": float(pedido.valor_pago),
                    }],
                    "back_urls": {
                        "success": settings.MERCADO_PAGO_SUCCESS_URL,
                        "failure": settings.MERCADO_PAGO_FAILURE_URL,
                    },
                    "auto_return": "approved",
                    "metadata": {"pagamento_id": pagamento.id}
                }

                preference_response = sdk.preference().create(preference_data)
                if preference_response.get("status") != 201:
                    return HttpResponse("Erro ao criar preferência de pagamento", status=500)

                preference = preference_response.get("response", {})
                pagamento.transaction_code = preference["id"]
                pagamento.save()

                return redirect(preference["init_point"])

            return HttpResponse("Método de pagamento não suportado", status=400)

    except PedidoPagamento.DoesNotExist:
        return HttpResponse("Pedido não encontrado.", status=404)


@login_required
def detalhes_pedido(request, pedido_id):
    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Pedido já processado ou inválido.")

    if request.method == 'POST':
        return redirect('payment:confirmar_pagamento', pedido_id=pedido.id)

    return render(request, "payment/detalhes_pedido.html", {"pedido": pedido})


@login_required
def pedidos_pendentes(request):
    pedidos = PedidoPagamento.objects.filter(usuario=request.user, status='PENDENTE').order_by('-data_criacao')
    return render(request, "payment/pedidos_pendentes.html", {"pedidos": pedidos})


@login_required
def cancelar_pedido(request, pedido_id):
    if request.method != 'POST':
        return HttpResponse("Método não permitido", status=405)

    pedido = get_object_or_404(PedidoPagamento, id=pedido_id, usuario=request.user)

    if pedido.status != 'PENDENTE':
        return HttpResponse("Este pedido não pode ser cancelado.", status=400)

    pedido.status = 'CANCELADO'
    pedido.save()

    messages.success(request, "Pedido cancelado com sucesso.")
    return redirect('payment:pedidos_pendentes')


def expirar_pedidos_antigos():
    limite = now() - timedelta(hours=48)
    PedidoPagamento.objects.filter(status='PENDENTE', data_criacao__lt=limite).update(status='EXPIRADO')


def processar_pedidos_aprovados():
    pagamentos = Pagamento.objects.filter(status='approved', creditado=False)
    for pagamento in pagamentos:
        try:
            Wallet.creditar(pagamento.usuario, pagamento.pedido_pagamento.moedas_geradas)
            pagamento.creditado = True
            pagamento.save()
        except Exception as e:
            # Logar ou tratar o erro de alguma forma
            print(f"Erro ao creditar pagamento {pagamento.id}: {e}")
