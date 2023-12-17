from django.shortcuts import render, HttpResponse, get_object_or_404
from .models import Category, Product
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

