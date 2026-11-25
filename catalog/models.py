from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField('Название категории', max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Mechanic(models.Model):
    full_name = models.CharField('ФИО механика', max_length=150)
    specialization = models.CharField('Специализация', max_length=150)
    experience = models.PositiveIntegerField(
        'Стаж, лет', validators=[MinValueValidator(0), MaxValueValidator(60)]
    )

    class Meta:
        verbose_name = 'Механик'
        verbose_name_plural = 'Механики'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    @property
    def initials(self):
        parts = self.full_name.split()
        return ''.join(p[0].upper() for p in parts[:2])

    @property
    def experience_percent(self):
        return min(int(self.experience / 12 * 100), 100)


class Service(models.Model):
    title = models.CharField('Название услуги', max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT,
        related_name='services', verbose_name='Категория'
    )
    mechanic = models.ForeignKey(
        Mechanic, on_delete=models.PROTECT,
        related_name='services', verbose_name='Механик'
    )
    price = models.DecimalField(
        'Цена, ₽', max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    duration_minutes = models.PositiveIntegerField(
        'Длительность, мин',
        validators=[MinValueValidator(15), MaxValueValidator(480)]
    )
    description = models.TextField('Описание', blank=True)
    image = models.ImageField('Фото', upload_to='services/', blank=True, null=True)
    created_at = models.DateTimeField('Добавлено', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'
        ordering = ['-created_at']

    def __str__(self):
        return self.title