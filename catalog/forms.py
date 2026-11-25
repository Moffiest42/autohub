from django import forms
from .models import Service


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'title', 'mechanic', 'price',
                  'duration_minutes', 'description', 'image']
        help_texts = {
            'duration_minutes': 'От 15 до 480 минут.',
            'price': 'Стоимость в рублях, больше нуля.',
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 3:
            raise forms.ValidationError('Название должно содержать минимум 3 символа.')
        return title

    def clean_price(self):
        price = self.cleaned_data['price']
        if price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля.')
        if price > 1_000_000:
            raise forms.ValidationError('Цена не может превышать 1 000 000 ₽.')
        return price

    def clean_duration_minutes(self):
        duration = self.cleaned_data['duration_minutes']
        if not 15 <= duration <= 480:
            raise forms.ValidationError('Длительность должна быть от 15 до 480 минут.')
        return duration