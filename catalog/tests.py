from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User

from .models import Category, Mechanic, Service


class CatalogTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_user(
            username='admin_test', password='Pass12345!',
            full_name='Админ Тест', role='ADMIN', email='admin_test@test.ru')
        cls.user = User.objects.create_user(
            username='user_test', password='Pass12345!',
            full_name='Юзер Тест', email='user_test@test.ru')
        cls.category = Category.objects.create(name='Диагностика')
        cls.other_category = Category.objects.create(name='Ремонт')
        cls.mechanic = Mechanic.objects.create(
            full_name='Максим Крылов', specialization='Электрика', experience=7)
        cls.service = Service.objects.create(
            title='Компьютерная диагностика', category=cls.category,
            mechanic=cls.mechanic, price=Decimal('1800.00'), duration_minutes=45)

    def valid_payload(self, **overrides):
        data = {
            'category': self.category.pk,
            'title': 'Замена масла и фильтров',
            'mechanic': self.mechanic.pk,
            'price': '900.00',
            'duration_minutes': '40',
            'description': 'Замена масла и фильтра',
        }
        data.update(overrides)
        return data

    def test_pages_available(self):
        for name in ['home', 'service_list', 'contacts', 'register', 'login']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 200)

    def test_detail_page(self):
        response = self.client.get(reverse('service_detail', args=[self.service.pk]))
        self.assertContains(response, 'Компьютерная диагностика')

    def test_missing_id_returns_404(self):
        self.assertEqual(self.client.get(reverse('service_detail', args=[9999])).status_code, 404)

    def test_anonymous_cannot_create(self):
        response = self.client.get(reverse('service_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_regular_user_cannot_create(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('service_create')).status_code, 403)

    def test_admin_create_inserts_row(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('service_create'), self.valid_payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Service.objects.count(), 2)

    def test_empty_required_fields_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('service_create'), {'title': ''})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.count(), 1)
        self.assertTrue(response.context['form'].errors)

    def test_negative_price_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('service_create'), self.valid_payload(price='-5'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.count(), 1)
        self.assertIn('price', response.context['form'].errors)

    def test_duration_out_of_range_rejected(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('service_create'), self.valid_payload(duration_minutes='5'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Service.objects.count(), 1)

    def test_search_and_category_filter(self):
        self.assertContains(self.client.get(reverse('service_list'), {'q': 'диагностика'}), 'Компьютерная')
        self.assertNotContains(self.client.get(reverse('service_list'), {'q': 'масло'}), 'Компьютерная')
        response = self.client.get(reverse('service_list'), {'category': self.other_category.pk})
        self.assertEqual(len(response.context['services']), 0)

    def test_admin_update_changes_row(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('service_update', args=[self.service.pk]),
                         self.valid_payload(title='Диагностика электрики'))
        self.service.refresh_from_db()
        self.assertEqual(self.service.title, 'Диагностика электрики')

    def test_admin_delete_removes_row(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('service_delete', args=[self.service.pk]))
        self.assertEqual(Service.objects.count(), 0)