from django.db import models

# Create your models here.

from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    age = models.IntegerField(blank=False, default=18)
    address = models.TextField(blank=True)

class Category(models.Model):
    name = models.CharField(max_length=100)
    preview = models.ImageField(upload_to ='uploads/previews/', blank=True)
    
    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT, blank=True)
    name = models.CharField(max_length=200)
    preview = models.ImageField(upload_to ='uploads/product-previews/', blank=True)
    description = models.TextField(blank=True, default="No description")
    price = models.FloatField(blank=True, default=0)
    wiki_link = models.TextField(blank=True, default="No wiki link")
    available = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE) 

    def __str__(self):
        return f"Корзина {self.user.first_name} {self.user.last_name}"

class ProductStack(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='products')
    product = models.ForeignKey(Product, on_delete=models.SET_DEFAULT, default=0)
    count = models.IntegerField(blank=False, default=1)

    def get_cost(self):
        return self.count * self.product.price

    def __str__(self):
        return f"{self.product} - {self.count} шт"
