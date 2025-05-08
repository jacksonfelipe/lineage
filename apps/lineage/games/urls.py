from django.urls import path
from . import views
from . import manager_box_views


app_name = "games"


urlpatterns = [
    path('roleta/', views.roulette_page, name='roulette_page'),
    path('roleta/spin-ajax/', views.spin_ajax, name='spin_ajax'),

    path('comprar-fichas/', views.comprar_fichas, name='comprar_fichas'),
    path('bag/dashboard/', views.bag_dashboard, name='bag_dashboard'),

    # Dashboard do User (boxes)
    path('box/dashboard/', views.box_dashboard_view, name='box_user_dashboard'),

    path('box/opening/', views.box_opening_home, name='box_opening_home'),
    path('box/buy_and_open/<int:box_type_id>/', views.buy_and_open_box_view, name='box_buy_and_open'),
    path('box/open_box/<int:box_id>/', views.open_box_view, name='box_user_open_box'),

    # Dashboard do Admin (boxes)
    path('box/manager/dashboard/', manager_box_views.dashboard, name='box_manager_dashboard'),

    path('box/manager/boxes/', manager_box_views.box_list_view, name='box_list'),
    path('box/manager/box/create/', manager_box_views.box_create_view, name='box_create'),
    path('box/manager/box/edit/<int:pk>/', manager_box_views.box_edit_view, name='box_edit'),
    path('box/manager/box/delete/<int:pk>/', manager_box_views.box_delete_view, name='box_delete'),

    path('box/manager/box-types/', manager_box_views.box_type_list_view, name='box_type_list'),
    path('box/manager/box-type/create/', manager_box_views.box_type_create_view, name='box_type_create'),
    path('box/manager/box-type/edit/<int:pk>/', manager_box_views.box_type_edit_view, name='box_type_edit'),
    path('box/manager/box-type/delete/<int:pk>/', manager_box_views.box_type_delete_view, name='box_type_delete'),

    path('box/manager/items/', manager_box_views.item_list_view, name='item_list'),
    path('box/manager/item/create/', manager_box_views.item_create_view, name='item_create'),
    path('box/manager/item/edit/<int:pk>/', manager_box_views.item_edit_view, name='item_edit'),
    path('box/manager/item/delete/<int:pk>/', manager_box_views.item_delete_view, name='item_delete'),
]
