from django.conf import settings
from django.db import models

from catalog.models import Service


class Appointment(models.Model):
    class Status(models.TextChoices):
        NEW = 'NEW', 'Новая'
        CONFIRMED = 'CONFIRMED', 'Подтверждена'
        IN_PROGRESS = 'IN_PROGRESS', 'В работе'
        DONE = 'DONE', 'Завершена'
        CANCELLED = 'CANCELLED', 'Отменена'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='appointments', verbose_name='Клиент')
    service = models.ForeignKey(Service, on_delete=models.PROTECT,
                                related_name='appointments', verbose_name='Услуга')
    car_info = models.CharField('Автомобиль (марка, модель, год)', max_length=150)
    date = models.DateField('Дата визита')
    time = models.TimeField('Время визита')
    phone = models.CharField('Телефон для связи', max_length=20)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField('Статус', max_length=12,
                              choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField('Создано', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Запись на обслуживание'
        verbose_name_plural = 'Записи на обслуживание'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.service} — {self.date} {self.time:%H:%M}'