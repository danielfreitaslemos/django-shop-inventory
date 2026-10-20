from django.urls import path

from . import views

urlpatterns = [
    path('lookup/', views.product_lookup, name='product_lookup'),
    path('manager/add/', views.add_product, name='add_product'),
    path('manager/dashboard', views.manager_dashboard, name='manager_dashboard')
]
