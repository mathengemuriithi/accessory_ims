from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('', views.dashboard_redirect, name='dashboard_redirect'),
    path('setup/', views.setup_view, name='setup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Admin
    path('admin-panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-panel/products/', views.products_list, name='products_list'),
    path('admin-panel/products/add/', views.product_add, name='product_add'),
    path('admin-panel/products/<int:pk>/edit/', views.product_edit, name='product_edit'),
    path('admin-panel/products/<int:pk>/delete/', views.product_delete, name='product_delete'),
    path('admin-panel/sales/', views.sales_history, name='sales_history'),
    path('admin-panel/sales/pdf/', views.sales_pdf, name='sales_pdf'),
    path('admin-panel/reconciliation/', views.reconciliation_list, name='reconciliation_list'),
    path('admin-panel/categories/', views.categories_list, name='categories_list'),
    path('admin-panel/users/', views.users_list, name='users_list'),

    # Attendant
    path('shop/', views.attendant_dashboard, name='attendant_dashboard'),
    path('shop/sell/<int:pk>/', views.sell_product, name='sell_product'),
    path('shop/reconcile/', views.reconciliation_form, name='reconciliation_form'),
]
