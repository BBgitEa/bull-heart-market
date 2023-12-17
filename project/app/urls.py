from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('category/<str:key>', views.category, name='category'),
    path('product/<str:key>', views.product, name='product'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.cart_add, name="cart_add"),
]