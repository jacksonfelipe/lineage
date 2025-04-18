from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    path('', views.shop_home, name='shop_home'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add-item/<int:item_id>/', views.add_item_to_cart, name='add_item_to_cart'),
    path('cart/add-package/<int:package_id>/', views.add_package_to_cart, name='add_package_to_cart'),
    path('cart/apply-promo/', views.apply_promo_code, name='apply_promo_code'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('purchases/', views.purchase_history, name='purchase_history'),

    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/items/', views.admin_items, name='admin_items'),
    path('admin/packages/', views.admin_packages, name='admin_packages'),
    path('admin/promotions/', views.admin_promotions, name='admin_promotions'),
]
