from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # =========================== API INFO ===========================
    path('', views.APIInfoView.as_view(), name='api_info'),
    
    # =========================== AUTHENTICATION ===========================
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    
    # =========================== USER ENDPOINTS ===========================
    path('user/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('user/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('user/dashboard/', views.UserDashboardView.as_view(), name='user_dashboard'),
    path('user/stats/', views.UserStatsView.as_view(), name='user_stats'),
    
    # =========================== SERVER STATUS ===========================
    path('server/status/', views.ServerStatusView.as_view(), name='server_status'),
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
    
    # =========================== SEARCH ENDPOINTS ===========================
    path('search/character/', views.CharacterSearchView.as_view(), name='character_search'),
    path('search/item/', views.ItemSearchView.as_view(), name='item_search'),
    
    # =========================== GAME DATA ===========================
    path('clan/<str:clan_name>/', views.ClanDetailView.as_view(), name='clan_detail'),
    path('auction/items/', views.AuctionItemsView.as_view(), name='auction_items'),
]
