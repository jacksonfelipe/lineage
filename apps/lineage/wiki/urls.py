from django.urls import path
from . import views

app_name = 'wiki'

urlpatterns = [
    path('', views.WikiHomeView.as_view(), name='home'),
    path('general/', views.WikiGeneralView.as_view(), name='general'),
    path('rates/', views.WikiRatesView.as_view(), name='rates'),
    path('raids/', views.WikiRaidsView.as_view(), name='raids'),
    path('assistance/', views.WikiAssistanceView.as_view(), name='assistance'),
    path('events/', views.WikiEventsView.as_view(), name='events'),
    path('updates/', views.WikiUpdatesView.as_view(), name='updates'),
    path('features/', views.WikiFeaturesView.as_view(), name='features'),
    path('page/<slug:slug>/', views.WikiPageDetailView.as_view(), name='page'),
    path('section/<int:pk>/', views.WikiSectionDetailView.as_view(), name='section'),
]
