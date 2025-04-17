from django.urls import path
from . import views


app_name = "inventory"


urlpatterns = [
    path('retirar/', views.retirar_item_servidor, name='retirar_item'),
    path('inserir-item/<str:char_name>/<int:item_id>/', views.inserir_item_servidor, name='inserir_item'),
    path('trocar/', views.trocar_item_com_jogador, name='trocar_item'),
    path('dashboard/', views.inventario_dashboard, name='inventario_dashboard'),
    path('global/', views.inventario_global, name='inventario_global')
]
