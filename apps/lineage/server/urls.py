from django.urls import path
from . import views
from .accounts_views import *

app_name = 'server'

urlpatterns = [
    path("api/players-online/", views.players_online, name="api_players_online"),
    path("api/top-pvp/", views.top_pvp, name="api_top_pvp"),
    path("api/top-pk/", views.top_pk, name="api_top_pk"),
    path("api/top-clan/", views.top_clan, name="api_top_clan"),
    path("api/top-rich/", views.top_rich, name="api_top_rich"),
    path("api/top-online/", views.top_online, name="api_top_online"),
    path("api/top-level/", views.top_level, name="api_top_level"),
    path("api/olympiad-ranking/", views.olympiad_ranking, name="api_olympiad_ranking"),
    path("api/olympiad-heroes/", views.olympiad_all_heroes, name="api_olympiad_all_heroes"),
    path("api/olympiad-current-heroes/", views.olympiad_current_heroes, name="api_olympiad_current_heroes"),
    path("api/grandboss-status/", views.grandboss_status, name="api_grandboss_status"),
    path("api/raidboss-status/", views.raidboss_status, name="api_raidboss_status"),
    path("api/siege/", views.siege, name="api_siege"),
    path("api/siege-participants/<int:castle_id>/", views.siege_participants, name="api_siege_participants"),
    path("api/boss-jewel-locations/", views.boss_jewel_locations, name="api_boss_jewel_locations"),

    path("api/config/", views.api_config_panel, name="api_config_panel"),

    path('account/update-password', update_password, name='update_password'),
    path('account/dashboard', account_dashboard, name='account_dashboard'),
    path('account/register', register_lineage_account, name='lineage_register'),
]
