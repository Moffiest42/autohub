from datetime import date as dt_date, datetime, time as dt_time

from django import forms

from .models import Appointment


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'car_info', 'date', 'time', 'phone', 'comment']
        widgets = {
            'date': forms.HiddenInput(),   # значение подставляет JS из видимого календаря
            'time': forms.HiddenInput(),   # значение подставляет JS из сетки слотов
            'phone': forms.TextInput(attrs={'inputmode': 'tel', 'placeholder': '+7 900 123-45-67'}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_date(self):
        d = self.cleaned_data['date']
        if d < dt_date.today():
            raise forms.ValidationError('Нельзя записаться на прошедшую дату.')
        return d

    def clean_phone(self):
        raw = self.cleaned_data['phone']
        digits = ''.join(ch for ch in raw if ch.isdigit())
        if len(digits) != 11 or digits[0] not in '78':
            raise forms.ValidationError('Формат телефона: +7 900 123-45-67.')
        return '+7' + digits[1:]

    def clean(self):
        cleaned = super().clean()
        d, t = cleaned.get('date'), cleaned.get('time')
        if d and t:
            if datetime.combine(d, t) <= datetime.now():
                self.add_error('time', 'Это время уже прошло — выберите другой слот.')
            weekday = d.weekday()  # 0 = понедельник
            if weekday == 6:
                self.add_error('date', 'Воскресенье — выходной, выберите другой день.')
            elif weekday == 5:
                if not dt_time(10, 0) <= t <= dt_time(16, 0):
                    self.add_error('time', 'В субботу доступно время с 10:00 до 16:00.')
            elif not dt_time(9, 0) <= t <= dt_time(18, 0):
                self.add_error('time', 'В будни доступно время с 09:00 до 18:00.')
        return cleaned