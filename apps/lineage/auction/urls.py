from django.urls import path
from . import views


app_name = "auction"


urlpatterns = [
    path('', views.listar_leiloes, name='listar_leiloes'),
    path('lance/<int:auction_id>/', views.fazer_lance, name='fazer_lance'),
    path('encerrar/<int:auction_id>/', views.encerrar_leilao, name='encerrar_leilao'),
]
