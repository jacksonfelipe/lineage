from django.urls import path
from .views import *
from .public import *


urlpatterns = [
    path('', index, name='index'),

    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/add-or-edit-address/', add_or_edit_address, name='add_or_edit_address'),
    path('profile/', profile, name='profile'),

    path('app/logs/info/', log_info_dashboard, name='log_info_dashboard'),
    path('app/logs/error/', log_error_dashboard, name='log_error_dashboard'),

    path('public/news/', public_news_list, name='public_news_list'),
    path('public/news/<slug:slug>/', public_news_detail, name='public_news_detail'),
    path('public/faq/', public_faq_list, name='public_faq_list'),

    path('accounts/logout/', logout_view, name="logout"),
]
