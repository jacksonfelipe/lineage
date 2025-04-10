from django.urls import path
from . import views


app_name = "payment"


urlpatterns = [
    path('purchase/', views.purchase, name='purchase'),
    path('confirmar-pagamento/<str:valor>/<str:metodo>/', views.confirmar_pagamento, name='confirmar_pagamento'),
    path('mercadopago/sucesso/', views.pagamento_sucesso, name='pagamento_sucesso'),
    path('mercadopago/erro/', views.pagamento_erro, name='pagamento_erro'),
    path('mercadopago/notificacao/', views.notificacao_mercado_pago, name='notificacao_mercado_pago'),
]
