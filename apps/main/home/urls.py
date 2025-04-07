from django.urls import path
from .views import *
from .public import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', index, name='index'),
    path('pages/dashboard/', dashboard, name="dashboard"),

    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/add-or-edit-address/', add_or_edit_address, name='add_or_edit_address'),
    path('profile/', profile, name='profile'),

    path('app/logs/info/', log_info_dashboard, name='log_info_dashboard'),
    path('app/logs/error/', log_error_dashboard, name='log_error_dashboard'),

    path('public/news/', public_news_list, name='public_news_list'),
    path('public/news/<slug:slug>/', public_news_detail, name='public_news_detail'),
    path('public/faq/', public_faq_list, name='public_faq_list'),


    # Authentication
    path('accounts/register/', register_view, name="register"),
    path('accounts/login/', UserLoginView.as_view(), name="login"),
    path('accounts/logout/', logout_view, name="logout"),
    path('accounts/password-change/', UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts_custom/password-change-done.html'), name="password_change_done"),
    path('accounts/password-reset/', UserPasswordResetView.as_view(), name="password_reset"),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', UserPasswrodResetConfirmView.as_view(), name="password_reset_confirm"),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(template_name='accounts_custom/password-reset-done.html'), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='accounts_custom/password-reset-complete.html'), name='password_reset_complete'),
    path('accounts/lock/', lock, name="lock"),
]
