from django.shortcuts import render, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Category, Product, Cart, ProductStack

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


@login_required
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    product_stacks = cart.products.all()
    return render(request, "cart.html", {
            'username': request.user,
            'product_stacks': product_stacks,
    })


@login_required
def cart_add(request):
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


@login_required
def cart_delete(request):
    product_stack = get_product_stack_from_request(request)
    try:
        product_stack.delete()
    except:
        return responces['error']
    return responces['success']


@login_required
def cart_change(request):
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