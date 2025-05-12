from django.urls import path
from . import views
from . import mercadopago_views
from . import stripe_views


app_name = "payment"


urlpatterns = [
    path('new/', views.criar_ou_reaproveitar_pedido, name='novo_pedido'),
    path('order/<int:pedido_id>/', views.detalhes_pedido, name='detalhes_pedido'),
    path('order/<int:pedido_id>/confirm/', views.confirmar_pagamento, name='confirmar_pagamento'),
    path('pending/', views.pedidos_pendentes, name='pedidos_pendentes'),
    path('cancel-order/<int:pedido_id>/', views.cancelar_pedido, name='cancelar_pedido'),

    path('mercadopago/sucesso/', mercadopago_views.pagamento_sucesso, name='pagamento_sucesso'),
    path('mercadopago/erro/', mercadopago_views.pagamento_erro, name='pagamento_erro'),
    path('mercadopago/notificacao/', mercadopago_views.notificacao_mercado_pago, name='notificacao_mercado_pago'),

    path('stripe/sucesso/', stripe_views.stripe_pagamento_sucesso, name='stripe_pagamento_sucesso'),
    path('stripe/erro/', stripe_views.stripe_pagamento_erro, name='stripe_pagamento_erro'),
    path('stripe/webhook/', stripe_views.stripe_webhook, name='stripe_webhook'),
]
