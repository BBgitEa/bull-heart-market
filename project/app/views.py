from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
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
    return render(request, "product.html", {
        'product': product,
    })

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

def cart_add(request):
    if request.user.is_authenticated:
        product_id = request.POST['product_id']
        product_count = int(request.POST['count'])
        cart = request.user.cart
        product = get_object_or_404(Product, id = product_id)
        product_stack = cart.get_product_stack(product=product)
        if product_stack:
            product_stack.count += product_count
        else:
            product_stack = ProductStack(cart=cart, product=product, count=product_count)
        product_stack.save()
        return JsonResponse({'status': '200', 'message': 'Product added.'})
    else:
        return  JsonResponse({'status': '403', 'message': 'Not Authenticated.'})
