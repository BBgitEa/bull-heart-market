from django.shortcuts import render, HttpResponse, get_object_or_404
from django.http import JsonResponse
from .models import Category, Product, Cart, ProductStack
# Create your views here.

responces = {
    "success" : JsonResponse({'status': '200', 'message': 'Success.'}),
    "error" :  JsonResponse({'status': '404', 'message': 'Error occured'}),
    "no_auth" : JsonResponse({'status': '403', 'message': 'Not Authenticated.'}),
}

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
    if not request.user.is_authenticated:
        return responces['no_auth']
        
    product_count = int(request.POST['count'])
    product_id = request.POST['product_id']
    product = get_object_or_404(Product, id = product_id)
    cart = request.user.cart
    product_stack = cart.get_product_stack(product=product)
    if product_stack:
        product_stack.count += product_count
    else:
        product_stack = ProductStack(cart=cart, product=product, count=product_count)
    product_stack.save()
    return responces['success']


def cart_delete(request):
    if not request.user.is_authenticated:
        return responces['no_auth']
    
    product_stack = get_product_stack_from_request(request)
    try:
        product_stack.delete()
    except:
        return responces['error']
    return responces['success']


def cart_change(request):
    if not request.user.is_authenticated:
        return  responces['no_auth']
    
    product_count = int(request.POST['count'])
    product_stack = get_product_stack_from_request(request)
    product_stack.count = product_count
    product_stack.save()
    return responces['success']


def get_product_stack_from_request(request):
    product_id = request.POST['product_id']
    product = get_object_or_404(Product, id = product_id)
    cart = request.user.cart
    product_stack = cart.get_product_stack(product=product)
    return product_stack