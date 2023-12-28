"""Этот модуль содержит тесты приложения."""
from django.test import TestCase
from app.models import Product, User, get_crypted_key
from django.contrib.auth.models import Group
from app.views import messages
from django.shortcuts import HttpResponse
import datetime, hashlib, random


class LoginLogoutViewTests(TestCase):
    """Этот класс содержит тесты для представлений login и logout (Входа и выхода из аккаунта). """

    def setUp(self):
        self.user = User.objects.create_user('username', 'email@mail.com', 'password')
        self.user.save()

    def test_get_request_anonymus(self):
        """Этот тест проверяет отправку страницы входа не авторизированному пользователю. """

        response = self.client.get('/login/', follow=True)
        self.assertTemplateUsed(response, 'auth/login.html')
    
    def test_wrong_post_request(self):
        """Этот тест проверяет возвращение страницы с ошибкой на 
           неверные данные логина и пароля отправленные в POST запросе. 
        """
        cases = [
            {'username': '', 'password': ''}, #Пустые данные
            {'username': 'username', 'password': 'another_password'}, #Неправильный пароль
            {'username': 'another_username', 'password': 'password'}, #Несуществующее имя пользователя
            {'username': 'sdsdswewd34r33', 'password': 'ddddddddddddddddddfdfefewfewf'}, #Случайные данные
        ]
        for case in cases:
            with self.subTest():
                response = self.client.post('/login/', follow=True, data=case)
                self.assertContains(response, messages['wrong_login_data'])

    def test_valid_post_request(self):
        """Этот тест проверяет авторизацию и перенаправление на главную страницу после успешной авторизации"""

        response = self.client.post('/login/', follow=True, data={'username': 'username', 'password': 'password'})
        self.assertRedirects(response, '/')
    
    def test_get_request_authorized(self):
        """Этот тест проверяет перенаправление на главную страницу при запросе на представление входа
           если пользователь уже авторизован.
        """
        
        response = self.client.post('/login/', follow=True, data={'username': 'username', 'password': 'password'})
        with self.subTest():
            response = self.client.post('/login/', follow=True, data={})
            self.assertRedirects(response, '/')
        with self.subTest():
            response = self.client.get('/login/', follow=True)
            self.assertRedirects(response, '/')
    
    def test_logout(self):
        """Этот тест проверяет 'разлогинивание' пользователя и перенаправление на страницу входа."""

        response = self.client.get('/logout/', follow=True)
        self.assertRedirects(response, '/login/')


class SignupViewTests(TestCase):
    """Этот класс содержит тесты для представления signup(Регистрации). """
    
    def setUp(self):
        self.customer_group = Group(name='Customer')
        self.customer_group.save()
        self.user = User.objects.create_user('username', 'email@mail.com', 'password')
        self.user.save()

    def test_get_request_anonymus(self):
        """Этот тест проверяет отправку страницы регистрации не авторизированному пользователю. """

        response = self.client.get('/signup/', follow=True)
        self.assertTemplateUsed(response, 'auth/signup.html')
    
    def test_wrong_post_request(self):
        """Этот тест проверяет возвращение страницы с ошибкой на 
           неккоректные данные отправленные в POST запросе. 
        """
        cases = [
            {'username': '', 'email': '', 'password': ''}, #Пустые данные
            {'username': 'username', 'email': 'any@mail.com', 'password': 'sdsdsdssd'}, #Чужое имя пользователя
            {'username': 'username2', 'email': 'email@mail.com', 'password': 'sdsdsd'}, #Чужая почта
            {'username': 'username', 'email': 'email@mail.com', 'password': 'sdsdsd'}, #Чужая почта и имя пользователя
            {'username': 'username2', 'email': 'good_email@mail.com', 'password': ''}, #Отсутствие одних из данных
            {'username': 'username2', 'email': 'good_email', 'password': 'some_password'}, #Неккоректный адрес почты
        ]
        for case in cases:
            with self.subTest():
                response = self.client.post('/signup/', follow=True, data=case)
                self.assertContains(response, messages['wrong_signup_data'])
    
    def test_get_request_authorized(self):
        """Этот тест проверяет перенаправление на главную авторизированному пользователю. """

        response = self.client.post('/login/', follow=True, data={'username': 'username', 'password': 'password'})
        with self.subTest():
            response = self.client.post('/signup/', follow=True, data={})
            self.assertRedirects(response, '/')
        with self.subTest():
            response = self.client.get('/signup/', follow=True)
            self.assertRedirects(response, '/')

    def test_valid_post_request(self):
        """Этот тест проверяет регистрацию пользователя и перенаправление на главную страницу"""

        user_data = {
            'username': 'newuser',
            'email': 'realygood@gmail.com',
            'password': 'good_password'
        }
        response = self.client.post('/signup/', follow=True, data=user_data)
        with self.subTest():
            user = User.objects.get(username=user_data['username'])
            self.assertEqual(user.username, user_data['username'])
            self.assertEqual(user.email, user_data['email'])
        with self.subTest():
            self.assertRedirects(response, '/')


class EmailActivationViewTests(TestCase):
    """Этот класс содержит тесты представления activation(Подтверждения почты). """

    def setUp(self):
        self.customer_group = Group(name='Customer')
        self.customer_group.save()
        user_data = {
            'username': 'newuser',
            'email': 'realygood@gmail.com',
            'password': 'good_password'
        }
        self.client.post('/signup/', follow=True, data=user_data)

    def test_email_activation_exists(self):
        """Этот тест проверяет создание записи подтверждения почты в базе данных после регистрации."""

        user = User.objects.get(username='newuser')
        self.assertNotEqual(user.activation, None)
    
    def test_email_activation_validation(self):
        """Этот тест проверяет подтверждение почты по переходу по ссылке с ключом."""

        user = User.objects.get(username='newuser')
        key = user.activation.key
        response = self.client.get('/activate/'+key, follow=True)
        self.assertNotEqual(response, HttpResponse('Вы успешно подтвердили аккаунт!'))

    def test_email_activation_timed_out(self):
        """Этот тест проверяет неудачное подтверждение почты по переходу по ссылке с ключом
           когда время действия ключа вышло.
        """

        user = User.objects.get(username='newuser')
        user.activation.expires_in = user.activation.expires_in - datetime.timedelta(seconds=86500)
        key = user.activation.key
        response = self.client.get('/activate/'+key, follow=True)
        self.assertNotEqual(response, HttpResponse('Ключ подтверждения больше не действителен.'))
    
    def test_email_activation_already_activated(self):
        """Этот тест проверяет неудачное подтверждение почты по переходу по ссылке с ключом
           когда аккаунт уже был подтвержден.
        """

        user = User.objects.get(username='newuser')
        key = user.activation.key
        response = self.client.get('/activate/'+key, follow=True)
        response = self.client.get('/activate/'+key, follow=True)
        self.assertNotEqual(response, HttpResponse('Ваш аккаунт уже подтвержден.'))
    
    def test_email_activation_wrong(self):
        """Этот тест проверяет возврат ошибки при отсутвии 
           в базе данных ключа подтверждения из запроса.
        """

        user = User.objects.get(username='newuser')
        key = get_crypted_key(str(random.random()))
        response = self.client.get('/activate/'+key, follow=True)
        self.assertEqual(response.status_code, 404)