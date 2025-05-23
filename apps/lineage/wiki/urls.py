from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    # Home
    path('public/wiki/', views.WikiHomeView.as_view(), name='home'),
    
    # General Information (New Structure)
    path('public/wiki/general/', views.WikiGeneralListView.as_view(), name='general_list'),
    path('public/wiki/general/<int:pk>/', views.WikiGeneralDetailView.as_view(), name='general_detail'),
    
    # Rates
    path('public/wiki/rates/', views.WikiRatesView.as_view(), name='rates'),
    
    # Raids (New Structure)
    path('public/wiki/raids/', views.WikiRaidListView.as_view(), name='raid_list'),
    path('public/wiki/raids/<int:pk>/', views.WikiRaidDetailView.as_view(), name='raid_detail'),
    
    # Assistance (New Structure)
    path('public/wiki/assistance/', views.WikiAssistanceListView.as_view(), name='assistance_list'),
    path('public/wiki/assistance/<int:pk>/', views.WikiAssistanceDetailView.as_view(), name='assistance_detail'),
    
    # Events
    path('public/wiki/events/', views.WikiEventsView.as_view(), name='events'),
    
    # Updates
    path('public/wiki/updates/', views.WikiUpdatesView.as_view(), name='updates'),
    
    # Features
    path('public/wiki/features/', views.WikiFeaturesView.as_view(), name='features'),
    
    # Pages and Sections
    path('public/wiki/page/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page'),
    path('public/wiki/section/<int:pk>/', views.WikiSectionDetailView.as_view(), name='section'),
]
