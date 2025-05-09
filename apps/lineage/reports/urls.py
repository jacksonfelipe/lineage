from django.urls import path
from . import views


app_name = "reports"


urlpatterns = [
    path('inventario/', views.relatorio_movimentacoes_inventario, name='relatorio_movimentacoes_inventario'),
    path('leiloes/', views.relatorio_leiloes, name='relatorio_leiloes'),
    path('compras/', views.relatorio_compras, name='relatorio_compras'),
]
