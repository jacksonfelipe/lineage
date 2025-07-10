from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # APIs públicas do servidor Lineage 2
    path('server/players-online/', views.PlayersOnlineView.as_view(), name='players_online'),
    path('server/top-pvp/', views.TopPvPView.as_view(), name='top_pvp'),
    path('server/top-pk/', views.TopPKView.as_view(), name='top_pk'),
    path('server/top-clan/', views.TopClanView.as_view(), name='top_clan'),
    path('server/top-rich/', views.TopRichView.as_view(), name='top_rich'),
    path('server/top-online/', views.TopOnlineView.as_view(), name='top_online'),
    path('server/top-level/', views.TopLevelView.as_view(), name='top_level'),
    path('server/olympiad-ranking/', views.OlympiadRankingView.as_view(), name='olympiad_ranking'),
    path('server/olympiad-heroes/', views.OlympiadAllHeroesView.as_view(), name='olympiad_all_heroes'),
    path('server/olympiad-current-heroes/', views.OlympiadCurrentHeroesView.as_view(), name='olympiad_current_heroes'),
    path('server/grandboss-status/', views.GrandBossStatusView.as_view(), name='grandboss_status'),
    path('server/siege/', views.SiegeView.as_view(), name='siege'),
    path('server/siege-participants/<int:castle_id>/', views.SiegeParticipantsView.as_view(), name='siege_participants'),
    path('server/boss-jewel-locations/', views.BossJewelLocationsView.as_view(), name='boss_jewel_locations'),
]
