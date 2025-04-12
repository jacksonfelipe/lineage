from django.urls import path
from .views import SolicitationDashboardView, SolicitationListView, SolicitationCreateView


app_name = 'solicitation'


urlpatterns = [
    path('', SolicitationListView.as_view(), name='solicitation_list'),
    path('create/', SolicitationCreateView.as_view(), name='create'),
    path('<str:protocol>/dashboard/', SolicitationDashboardView.as_view(), name='solicitation_dashboard'),
]
