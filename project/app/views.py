from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Category, Product, Cart, ProductStack
# Create your views here.

def index(request):
    categories = Category.objects.all()
    count = categories.count()
    return render(request, "index.html", {'categories': categories, 'count': count})

def category(request, key):
    category = get_object_or_404(Category, id=key)
    return HttpResponse(category.name)

def product(request, key):
    product = get_object_or_404(Product, id=key)
    return HttpResponse(product.name)

def cart(request):
    if request.user.is_authenticated:
        cart = get_object_or_404(Cart, user=request.user)
        product_stacks = cart.products.all()
        return render(request, "cart.html", {
            'username': request.user,
            'product_stacks': product_stacks,
        })
    else:
        return HttpResponse("Вы не вошли в аккаунт")