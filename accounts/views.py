from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from .forms import RegisterForm


def register(request):
    if request.user.is_authenticated:
        return redirect('my_appointments')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()          # пароль хешируется внутри Django
            login(request, user)        # сразу создаём сессию
            messages.success(request, f'Добро пожаловать, {user.full_name}!')
            return redirect('my_appointments')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})