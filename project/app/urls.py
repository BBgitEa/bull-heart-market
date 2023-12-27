from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('category/<str:key>', views.category, name='category'),
    path('about/', views.about, name='about'),
    path('product/<str:key>', views.product, name='product'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.cart_add, name="cart_add"),
    path('cart/delete/', views.cart_delete, name="cart_delete"),
    path('cart/change/', views.cart_change, name="cart_change"),
    path('login/', views.login_view, name = 'login'),
    path('logout/', views.logout_view, name = 'logout'),
    path('signup/', views.signup_view, name= 'signup'),
    path('activate/<str:key>', views.activation_view, name = 'activate'),
    path('order/new/', views.order_creation, name = 'order_creation'),
    path('order/<str:order_id>', views.order, name = 'order'),
]