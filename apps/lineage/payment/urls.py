from django.urls import path
from . import views


app_name = "payment"


urlpatterns = [
    path("buy/", views.buy_coins, name="buy_coins"),
    path("purchase/", views.purchase, name="purchase"),
]
