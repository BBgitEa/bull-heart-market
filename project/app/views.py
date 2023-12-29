"""Этот модуль содержит представления(контроллеры), используемые в приложении."""
from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.models import Group
from .models import Category, Product, Cart, ProductStack, User, EmailActivation, Order
import threading


responces = {
    "success" : JsonResponse({'status': '200', 'message': 'Success.'}),
    "error" :  JsonResponse({'status': '404', 'message': 'Error occured'}),
    "no_auth" : JsonResponse({'status': '403', 'message': 'Not Authenticated.'}),
}

messages = {
    'wrong_login_data': 'Неверные пароль или имя пользователя.',
    'wrong_signup_data': 'Введены неверные данные.'
}

def index(request):
    """Представление главной страницы. 
       Возвращает каталог с категориями по GET запросу."""

    categories = Category.objects.all()
    count = categories.count()
    return render(request, "index.html", {'categories': categories, 'count': count})


def about(request):
    """Представление страницы о компании. 
       Возвращает страницу с информацией о компании по GET запросу."""

    return render(request, "about.html")


def category(request, key):
    """Представление страницы категории. 
       Возвращает страницу категории с карточками с товарами по GET запросу."""

    category = get_object_or_404(Category, id=key)
    return render(request, 'category.html', context={'category': category})


def product(request, key):
    """Представление страницы товара. 
       Возвращает страницу товара с информацией о нем по GET запросу."""

    product = get_object_or_404(Product, id=key)
    return render(request, "product.html", {
        'product': product,
    })


@login_required
def cart(request):
    """Представление страницы корзины. Требует авторизации.
       Возвращает страницу корзины с товарами пользователя по GET запросу."""

    cart = get_object_or_404(Cart, user=request.user)
    product_stacks = cart.products.all()
    return render(request, "cart.html", {
            'username': request.user,
            'product_stacks': product_stacks,
            'cart' : cart,
    })


@login_required
def cart_add(request):
    """API добавления товара в корзину. Требует авторизации.
      По POST запросу добавляет стэк товара указанного кол-ва в корзину, если такой товар есть и
      возвращает JSONResponce с статусом 200."""

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
    """API для удаления товара из корзины. Требует авторизации.
       По POST запросу удаляет стэк товара, если он есть в корзине и
       возвращает JSONResponce с статусом 200 в случае успеха и 
       статусом 404 при ошибке"""

    product_stack = get_product_stack_from_request(request)
    try:
        product_stack.delete()
    except:
        return responces['error']
    return responces['success']


@login_required
def cart_change(request):
    """API для изменения количества товара в стэке в корзине. Требует авторизации."""

    product_count = int(request.POST['count'])
    product_stack = get_product_stack_from_request(request)
    product_stack.count = product_count
    product_stack.save()
    return responces['success']


def get_product_stack_from_request(request):
    """Вспомогательный метод для получения стэка товара
       из POST-запроса по id товара."""

    product_id = request.POST['product_id']
    product = get_object_or_404(Product, id = product_id)
    cart = request.user.cart
    product_stack = cart.get_product_stack(product=product)
    return product_stack


def login_view(request):
    """Представление авторизации на сайте.
       По GET запросу возвращает страницу входа на сайт.
       По POST запросу в случае успешного входа перенаправляет на главную страницу,
       в случае неудачи возращает страницу входа с сообщением об ошибке.
       Если пользователь авторизован, перенаправляет на главную."""

    if request.user.is_authenticated:
        return redirect(index)

    if request.method == 'GET':
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
    """Представление для выхода из аккаунта на сайте.
       По GET запросу разлогинивает пользователя и перенаправляет на страницу входа."""

    logout(request)
    return redirect(login_view)

def signup_view(request):
    """Представление для регистрации аккаунта на сайте.
       По GET запросу возвращает страницу регистрации на сайте.
       По POST запросу в случае успешного регистрации создает нового пользователя
       и отправляет на почту ссылку для подтверждения почты,
       в случае неудачи возращает страницу регистрации с сообщением об ошибке.
       Если пользователь авторизован, перенаправляет на главную."""

    if request.user.is_authenticated:
        return redirect(index)

    if request.method == 'GET':
        return render(request, 'auth/signup.html')

    username = request.POST['username']
    password = request.POST['password']
    email = request.POST['email']
        
    if username and password and email:
        try:
            validate_email(email)
        except ValidationError as e:
            return render(request, 'auth/signup.html', context= {
                'message': 'Введены неверные данные.',
                'last_username': username,
                'last_email': email,
            })

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
            activation.save()
            threading.Thread(target=activation.send_email).start()

            return redirect(index)
           
    return render(request, 'auth/signup.html', context= {
                'message': 'Введены неверные данные.',
                'last_username': username,
                'last_email': email,
    })


def activation_view(request, key):
    """Представление для активации почты.
       Если ключ действителен то подтверждает пользователя(user.is_active = True).
       Если ключ больше не действителен, то возвращает сообщение об ошибке.
       Если аккаунт уже подтвержден, то возвращает сообщение об ошибке."""

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
    """Вспомогательный метод, определяющий существует ли пользователь
       с заданным username и(или) email в базе данных.
       Возвращает True - если да, False - если нет."""

    invalidName = User.objects.filter(username=username).first()
    invalidEmail = User.objects.filter(email=email).first()
    if invalidName or invalidEmail:
        return True
    return False


@login_required
def order_creation(request):
    """Представление оформления заказа. Требует авторизацию.
       По GET запросу возвращает страницу оформления заказа.
       По POST запросу создает новый заказ с содержимым из корзины и 
       уведомляет об этом пользователя по почте, возвращает сообщение
       о оформлении в случае успеха."""
       
    summ = request.user.cart.get_summ()
    if request.method == 'GET':
        return render(request, 'order_creation.html', context={
            'products': request.user.cart.products.all(),
            'summ' : summ,
            })

    if request.method == 'POST':
        order = Order()
        order.status = 0 #active status
        order.customer = request.user
        order.save()
        order.products.add(*request.user.cart.products.all())
        order.save()
        threading.Thread(target=order.send_new_order_email).start()
        return HttpResponse('Заказ успешно оформлен.')


@login_required
def order(request, order_id):
    """Представление страницы конкретного заказа. Требует авторизацию.
       По GET запросу возвращает страницу заказа."""

    order = get_object_or_404(Order, id=order_id)
    is_seller = request.user.groups.filter(name='Seller').exists()
    if is_seller:
        return render(request, 'order.html', context={'order': order})
    else:
        try:
            request.user.orders.get(id=order_id)
        except:
            return HttpResponse('403 Forbidden')

    return render(request, 'order.html', context={'order': order})


@login_required
def order_list(request):
    """Представление страницы списка заказов Требует авторизацию.
       По GET запросу возвращает список заказов.
       Если пользователь имеет роль Customer, возвращает только его заказы.
       Если пользователь имеет роль Seller, возращает все заказы."""

    orders = Order.objects.filter(customer=request.user)
    is_seller = request.user.groups.filter(name='Seller').exists()
    all_orders = {}
    if is_seller:
        all_orders = Order.objects.all()
    return render(request, 'order_list.html', context={'orders': orders, 'is_seller': is_seller, 'all_orders': all_orders})