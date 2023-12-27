from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Category, Product, User, Cart, ProductStack, EmailActivation, Order
# Register your models here.

class ProductStackInline(admin.TabularInline):
    model = ProductStack

class CartAdmin(admin.ModelAdmin):
    inlines = [
        ProductStackInline,
    ]

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart, CartAdmin)
admin.site.register(ProductStack)
admin.site.register(User, UserAdmin)
admin.site.register(EmailActivation)
admin.site.register(Order)