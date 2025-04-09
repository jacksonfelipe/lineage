from django.urls import path
from . import views

app_name = 'server'

urlpatterns = [
    path("api/players-online/", views.players_online, name="api_players_online"),
    path("api/top-pvp/", views.top_pvp, name="api_top_pvp"),
    path("api/top-pk/", views.top_pk, name="api_top_pk"),
    path("api/top-clan/", views.top_clan, name="api_top_clan"),
    path("api/top-rich/", views.top_rich, name="api_top_rich"),
]
