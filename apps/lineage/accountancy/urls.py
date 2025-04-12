from django.urls import path
from . import views


app_name = "accountancy"


urlpatterns = [
    path('', views.dashboard_accountancy, name='dashboard'),
    path('relatorio-saldo/', views.relatorio_saldo_usuarios, name='relatorio_saldo'),
    path('relatorio-fluxo-caixa/', views.relatorio_fluxo_caixa, name='relatorio_fluxo_caixa'),
    path('relatorio-pedidos-pagamentos/', views.relatorio_pedidos_pagamentos, name='relatorio_pedidos_pagamentos'),
    path('relatorio-reconciliacao-wallet/', views.relatorio_reconciliacao_wallet, name='relatorio_reconciliacao_wallet'),
]
