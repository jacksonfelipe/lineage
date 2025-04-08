from django.urls import path
from .views import SolicitationDashboardView, SolicitationListView, SolicitationCreateView


app_name = 'solicitation'


urlpatterns = [
    path('solicitation/', SolicitationListView.as_view(), name='solicitation_list'),
    path('solicitation/create/', SolicitationCreateView.as_view(), name='create'),
    path('solicitation/<str:protocol>/dashboard/', SolicitationDashboardView.as_view(), name='solicitation_dashboard'),
]
