from django.urls import path
from . import views


app_name = "games"


urlpatterns = [
    path('roleta/', views.roulette_page, name='roulette_page'),
    path('roleta/spin-ajax/', views.spin_ajax, name='spin_ajax'),
]
