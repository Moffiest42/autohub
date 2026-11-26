from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Category, Mechanic, Service

from .models import Appointment


def next_weekday():
    d = date.today() + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


class BookingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='client1', password='Pass12345!',
            full_name='Клиент Один', email='c1@test.ru')
        cls.other = User.objects.create_user(
            username='client2', password='Pass12345!',
            full_name='Клиент Два', email='c2@test.ru')
        cls.admin = User.objects.create_user(
            username='boss', password='Pass12345!',
            full_name='Админ', role='ADMIN', email='boss@test.ru')
        category = Category.objects.create(name='Диагностика')
        mechanic = Mechanic.objects.create(
            full_name='Максим Крылов', specialization='Электрика', experience=7)
        cls.service = Service.objects.create(
            title='Компьютерная диагностика', category=category,
            mechanic=mechanic, price=Decimal('1800.00'), duration_minutes=45)

    def payload(self, **overrides):
        data = {
            'service': self.service.pk,
            'car_info': 'Toyota Camry 2021',
            'date': next_weekday().isoformat(),
            'time': '10:00',
            'phone': '+79001234567',
            'comment': '',
        }
        data.update(overrides)
        return data

    def make_appointment(self, user=None, **overrides):
        data = self.payload(**overrides)
        return Appointment.objects.create(
            user=user or self.user, service=self.service,
            car_info=data['car_info'], date=data['date'],
            time=data['time'], phone=data['phone'])

    def test_booking_requires_login(self):
        response = self.client.get(reverse('booking'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_create_appointment(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('booking'), self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(Appointment.objects.first().user, self.user)
        self.assertEqual(Appointment.objects.first().status, 'NEW')

    def test_past_date_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('booking'),
                                    self.payload(date=(date.today() - timedelta(days=1)).isoformat()))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_bad_phone_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse('booking'), self.payload(phone='123'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 0)

    def test_user_sees_only_own(self):
        self.make_appointment(self.user)
        self.make_appointment(self.other)
        self.client.force_login(self.user)
        response = self.client.get(reverse('my_appointments'))
        self.assertEqual(len(response.context['appointments']), 1)

    def test_cannot_edit_foreign_id(self):
        foreign = self.make_appointment(self.other)
        self.client.force_login(self.user)
        response = self.client.get(reverse('appointment_update', args=[foreign.pk]))
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_foreign_id(self):
        foreign = self.make_appointment(self.other)
        self.client.force_login(self.user)
        response = self.client.post(reverse('appointment_delete', args=[foreign.pk]))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_confirmed_cannot_be_edited(self):
        own = self.make_appointment(self.user, status='CONFIRMED')
        self.client.force_login(self.user)
        response = self.client.get(reverse('appointment_update', args=[own.pk]))
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_open_admin_panel(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('admin_panel')).status_code, 403)

    def test_user_cannot_set_status_even_by_post(self):
        own = self.make_appointment(self.user)
        self.client.force_login(self.user)
        response = self.client.post(reverse('appointment_set_status', args=[own.pk]),
                                    {'status': 'DONE'})
        self.assertEqual(response.status_code, 403)
        own.refresh_from_db()
        self.assertEqual(own.status, 'NEW')

    def test_admin_sees_all_and_changes_status(self):
        a = self.make_appointment(self.user)
        self.make_appointment(self.other)
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin_panel'))
        self.assertEqual(len(response.context['appointments']), 2)
        self.client.post(reverse('appointment_set_status', args=[a.pk]), {'status': 'CONFIRMED'})
        a.refresh_from_db()
        self.assertEqual(a.status, 'CONFIRMED')

    def test_invalid_status_value_rejected(self):
        a = self.make_appointment(self.user)
        self.client.force_login(self.admin)
        self.client.post(reverse('appointment_set_status', args=[a.pk]), {'status': 'HACKED'})
        a.refresh_from_db()
        self.assertEqual(a.status, 'NEW')

    def test_logout_ends_session(self):
        self.client.force_login(self.user)
        self.client.post(reverse('logout'))
        response = self.client.get(reverse('my_appointments'))
        self.assertEqual(response.status_code, 302)