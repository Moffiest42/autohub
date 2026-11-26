from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='ivan', password='StrongPass123',
            full_name='Иван Иванов', email='ivan@test.ru')

    def register_payload(self, **overrides):
        data = {
            'full_name': 'Пётр Петров',
            'username': 'petr',
            'email': 'petr@test.ru',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        }
        data.update(overrides)
        return data

    def test_registration_creates_user_with_hashed_password(self):
        response = self.client.post(reverse('register'), self.register_payload())
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='petr')
        self.assertNotEqual(user.password, 'StrongPass123')
        self.assertTrue(user.password.startswith('pbkdf2_'))
        self.assertEqual(user.role, 'USER')

    def test_duplicate_username_rejected(self):
        response = self.client.post(reverse('register'), self.register_payload(username='ivan'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_duplicate_email_rejected(self):
        response = self.client.post(reverse('register'), self.register_payload(email='ivan@test.ru'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_short_password_rejected(self):
        response = self.client.post(reverse('register'),
                                    self.register_payload(password1='123', password2='123'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)

    def test_login_by_username(self):
        self.assertTrue(self.client.login(username='ivan', password='StrongPass123'))

    def test_login_by_email(self):
        response = self.client.post(reverse('login'),
                                    {'username': 'ivan@test.ru', 'password': 'StrongPass123'})
        self.assertEqual(response.status_code, 302)

    def test_wrong_password_rejected(self):
        response = self.client.post(reverse('login'),
                                    {'username': 'ivan', 'password': 'wrong'})
        self.assertEqual(response.status_code, 200)