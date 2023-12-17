from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name = 'index'),
    path('category/<str:key>', views.category, name='category'),
    path('product/<str:key>', views.product, name='product')
]