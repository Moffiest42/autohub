from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class RegisterForm(UserCreationForm):
    full_name = forms.CharField(label='ФИО', max_length=150)
    email = forms.EmailField(label='Email')

    class Meta:
        model = User
        fields = ['full_name', 'username', 'email', 'password1', 'password2']
        labels = {'username': 'Логин'}
        help_texts = {'username': 'Буквы, цифры и символы @/./+/-/_.'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Минимум 8 символов, не только цифры.'
        self.fields['password2'].help_text = 'Повторите пароль для проверки.'

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже зарегистрирован.')
        return email


class LoginOrEmailForm(AuthenticationForm):
    """Вход по логину ИЛИ email (п.5 методички)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин или Email'

    def clean_username(self):
        value = self.cleaned_data.get('username', '')
        if '@' in value:
            user = User.objects.filter(email__iexact=value).first()
            if user:
                return user.username
        return value