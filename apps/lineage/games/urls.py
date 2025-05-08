from django.urls import path
from . import views
from . import manager_box_views


app_name = "games"


urlpatterns = [
    path('roleta/', views.roulette_page, name='roulette_page'),
    path('roleta/spin-ajax/', views.spin_ajax, name='spin_ajax'),

    path('comprar-fichas/', views.comprar_fichas, name='comprar_fichas'),

    path('box/open_box/<int:box_id>/', views.open_box_view, name='box_user_open_box'),
    path('box/dashboard/', views.box_dashboard_view, name='box_user_dashboard'),

    # Dashboard do Admin
    path('box/manager/dashboard/', manager_box_views.dashboard, name='box_manager_dashboard'),

    path('box/manager/boxes/', manager_box_views.box_list_view, name='box_list'),
    path('box/manager/box/create/', manager_box_views.box_create_view, name='box_create'),
    path('box/manager/box/edit/<int:pk>/', manager_box_views.box_edit_view, name='box_edit'),
    path('box/manager/box/delete/<int:pk>/', manager_box_views.box_delete_view, name='box_delete'),

    path('box/manager/box-types/', manager_box_views.box_type_list_view, name='box_type_list'),
    path('box/manager/box-type/create/', manager_box_views.box_type_create_view, name='box_type_create'),
    path('box/manager/box-type/edit/<int:pk>/', manager_box_views.box_type_edit_view, name='box_type_edit'),
    path('box/manager/box-type/delete/<int:pk>/', manager_box_views.box_type_delete_view, name='box_type_delete'),

    path('box/manager/box-item/<int:box_type_id>/items/', manager_box_views.box_item_list_view, name='box_item_list'),
    path('box/manager/box-item/<int:box_type_id>/item/create/', manager_box_views.box_item_create_view, name='box_item_create'),
    path('box/manager/box-item/<int:box_type_id>/item/edit/<int:pk>/', manager_box_views.box_item_edit_view, name='box_item_edit'),
    path('box/manager/box-item/<int:box_type_id>/item/delete/<int:pk>/', manager_box_views.box_item_delete_view, name='box_item_delete'),
]

