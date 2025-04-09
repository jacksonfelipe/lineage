from django.urls import path
from . import views

app_name = 'wallet'

urlpatterns = [
    path('dashboard/', views.dashboard_wallet, name='dashboard'),
]
