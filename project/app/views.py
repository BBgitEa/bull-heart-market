from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import Group
from .models import Category, Product, Cart, ProductStack, User, EmailActivation

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


def login_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(index)
        return render(request, 'auth/login.html')

    username = request.POST['username']
    password = request.POST['password']
        
    if username and password:
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect(index)

    return render(request, 'auth/login.html', context= {
                'message':  'Неверные пароль или имя пользователя.',
                'last_username': username,
    })

def logout_view(request):
    logout(request)
    return redirect(index)

def signup_view(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return redirect(index)
        return render(request, 'auth/signup.html')

    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
        
    if username and password and email:
        try:
            validate_email(email)
        except ValidationError as e:
            pass

        if not is_user_exist(username, email):
            user = User.objects.create_user(username, email, password)
            group = Group.objects.get(name='Customer')
            user.groups.add(group)
            user.is_active = False
            cart = Cart()
            cart.user = user
            user.save()
            cart.save()

            activation = EmailActivation()
            activation.user = user
            activation.generate_key()
            activation.send_email()
            activation.save()


            return redirect(index)
           
    return render(request, 'auth/signup.html', context= {
                'message': 'Введены неверные данные.',
                'last_username': username,
                'last_email': email,
    })


def activation_view(request, key):
    email_activation = get_object_or_404(EmailActivation, key = key)
    if not email_activation.user.is_active:
        if timezone.now() > email_activation.expires_in:
            return HttpResponse('Ключ подтверждения больше не действителен.')
        else:
            email_activation.user.is_active = True
            email_activation.user.save()
            email_activation.delete()
            return HttpResponse('Вы успешно подтвердили аккаунт!')
    else:
        return HttpResponse('Ваш аккаунт уже подтвержден.')


def is_user_exist(username, email):
    invalidName = User.objects.filter(username=username).first()
    invalidEmail = User.objects.filter(email=email).first()
    print(invalidName, invalidEmail)
    if invalidName or invalidEmail:
        return True
    return False