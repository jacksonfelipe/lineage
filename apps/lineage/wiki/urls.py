from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    # Home
    path('public/wiki/', views.WikiHomeView.as_view(), name='home'),
    
    # General Information
    path('public/wiki/general/', views.WikiGeneralView.as_view(), name='general'),
    path('public/wiki/general/<int:pk>/', views.WikiGeneralDetailView.as_view(), name='general_detail'),
    
    # Rates
    path('public/wiki/rates/', views.WikiRatesView.as_view(), name='rates'),
    
    # Raids
    path('public/wiki/raids/', views.WikiRaidsView.as_view(), name='raids'),
    path('public/wiki/raids/<int:pk>/', views.WikiRaidDetailView.as_view(), name='raid_detail'),
    
    # Assistance
    path('public/wiki/assistance/', views.WikiAssistanceView.as_view(), name='assistance'),
    
    # Events
    path('public/wiki/events/', views.WikiEventsView.as_view(), name='events'),
    
    # Updates
    path('public/wiki/updates/', views.WikiUpdatesView.as_view(), name='updates'),
    
    # Features
    path('public/wiki/features/', views.WikiFeaturesView.as_view(), name='features'),
    
    # Pages and Sections
    path('public/wiki/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page'),
    path('public/wiki/section/<int:pk>/', views.WikiSectionDetailView.as_view(), name='section'),
]
