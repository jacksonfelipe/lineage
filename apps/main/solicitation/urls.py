from django.urls import path
from .views import CreditSolicitationDashboardView, CreditSolicitationListView


app_name = 'solicitation'


urlpatterns = [
    path('solicitation/', CreditSolicitationListView.as_view(), name='credit_solicitation_list'),
    path('solicitation/<str:protocol>/dashboard/', CreditSolicitationDashboardView.as_view(), name='credit_solicitation_dashboard'),
]
