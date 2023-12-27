from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import make_aware
from django.urls import reverse
import datetime, hashlib, random

class User(AbstractUser):
    age = models.IntegerField(blank=False, default=18)
    address = models.TextField(blank=True)


class Category(models.Model):
    name = models.CharField(max_length=100)
    preview = models.ImageField(upload_to ='uploads/previews/', blank=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('category',  args=[str(self.id)])


class EmailActivation(models.Model):
    user = models.OneToOneField(User, related_name = 'activation', on_delete = models.CASCADE)
    key = models.CharField(max_length=64)
    expires_in = models.DateTimeField()

    def send_email(self):
        link = settings.DOMAIN_NAME + '/activate/' + self.key
        message = 'Активируйте свой аккаунт: ' + link
        send_mail(
            'Активация аккаута | Bull Heart',
            message,
            'bullheartoff <no-reply@gmail.com',
            [self.user.email],
            fail_silently= False
        )

    def generate_key(self):
        self.key = get_crypted_key(self.user.username)
        self.expires_in = get_future_date(86400)


class Product(models.Model):
    category = models.ForeignKey(Category, related_name="products", on_delete=models.PROTECT, blank=True)
    name = models.CharField(max_length=200)
    preview = models.ImageField(upload_to ='uploads/product-previews/', blank=True)
    description = models.TextField(blank=True, default="No description")
    price = models.FloatField(blank=True, default=0)
    wiki_link = models.TextField(blank=True, default="No wiki link")
    available = models.BooleanField(default=False)
    count = models.IntegerField(blank=False, default=0)
    
    def __str__(self):
        return self.name

    def get_short_description(self):
        return str(self.description)[:100] + "..."

    def get_absolute_url(self):
        return reverse('product',  args=[str(self.id)])


class Cart(models.Model):
    user = models.OneToOneField(User, related_name='cart', on_delete=models.CASCADE) 
    
    def get_product_stack(self,product):
        try:
            return self.products.get(product = product)
        except: 
            return None


    def get_summ(self):
        s = 0
        for prod in self.products.all():
            s += int(prod.count) * float(prod.product.price)
            print(s)
        return s
    

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


class Order(models.Model):
    customer = models.ForeignKey(User, related_name="orders", on_delete=models.CASCADE, blank=True)
    products = models.ManyToManyField(ProductStack, related_name='orders', blank=True)
    statuses = {
        0 : 'active',
        1 : 'finished',
        2 : 'canceled'
    }
    status = models.IntegerField(choices=statuses, blank=False, default=0)
    creation_date = models.DateTimeField(auto_now_add=True)
    finish_date = models.DateTimeField(blank=True, null=True)

    def get_summ(self):
        s = 0
        for prod in self.products.all():
            s += prod.count * prod.product.price
        return s

    def send_new_order_email(self):
        send_mail(
            'Активация аккаута | Bull Heart',
            'Заказ успешно оформлен! Просмотреть можно по ссылке:',
            'bullheartoff <no-reply@gmail.com',
            [self.customer.email],
            fail_silently= False
        )

def get_crypted_key(value):
    salt = hashlib.sha256(str(random.random()).encode()).hexdigest()[:10]
    key = hashlib.sha256((salt+value).encode()).hexdigest()
    return key  

def get_future_date(time):
    date = datetime.datetime.now() + datetime.timedelta(seconds=time)
    return make_aware(date)

