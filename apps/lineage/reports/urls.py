from django.urls import path
from . import views


app_name = "reports"


urlpatterns = [
    path('inventory/movimentacoes-inventario/', views.relatorio_movimentacoes_inventario, name='relatorio_movimentacoes_inventario'),
]
