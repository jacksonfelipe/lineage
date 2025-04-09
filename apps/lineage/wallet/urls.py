from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('dashboard/', views.dashboard_wallet, name='dashboard'),
    path('transfer/servidor/', views.transfer_to_server, name='transfer_to_server'),
    path('transfer/jogador/', views.transfer_to_player, name='transfer_to_player'),
]
