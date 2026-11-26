from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.decorators import admin_required

from .forms import AppointmentForm
from .models import Appointment


@login_required
def booking(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user      # владелец — из сессии, НЕ из формы
            appointment.save()                   # INSERT
            messages.success(request,
                             f'Заявка №{appointment.pk} создана: {appointment.service}, '
                             f'{appointment.date:%d.%m.%Y} в {appointment.time:%H:%M}.')
            return redirect('my_appointments')
    else:
        initial = {'phone': request.user.phone}
        service_id = request.GET.get('service', '')
        if service_id.isdigit():
            initial['service'] = service_id
        form = AppointmentForm(initial=initial)
    return render(request, 'booking/booking.html', {'form': form})


@login_required
def my_appointments(request):
    # READ: SELECT ... WHERE user_id = текущий пользователь — чужих записей не видно
    appointments = (Appointment.objects
                    .filter(user=request.user)
                    .select_related('service', 'service__mechanic'))
    return render(request, 'booking/my_appointments.html', {'appointments': appointments})


@login_required
def appointment_update(request, pk):
    # подмена id в URL → 404: ищем только СРЕДИ СВОИХ записей
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    if appointment.status != Appointment.Status.NEW:
        raise PermissionDenied('Изменить можно только новую заявку. Для переноса позвоните нам.')
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()                          # UPDATE
            messages.success(request, 'Заявка обновлена.')
            return redirect('my_appointments')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'booking/booking.html', {'form': form, 'editing': appointment})


@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, user=request.user)
    if appointment.status in (Appointment.Status.IN_PROGRESS,
                              Appointment.Status.DONE,
                              Appointment.Status.CANCELLED):
        raise PermissionDenied('Эту заявку уже нельзя отменить онлайн.')
    if request.method == 'POST':
        appointment.delete()                     # DELETE
        messages.success(request, 'Заявка отменена.')
        return redirect('my_appointments')
    return render(request, 'booking/appointment_confirm_delete.html',
                  {'appointment': appointment})


@admin_required
def admin_panel(request):
    appointments = Appointment.objects.select_related('user', 'service', 'service__mechanic')
    status = request.GET.get('status', '')
    if status in Appointment.Status.values:
        appointments = appointments.filter(status=status)
    return render(request, 'booking/admin_panel.html', {
        'appointments': appointments,
        'statuses': Appointment.Status.choices,
        'active_status': status,
    })


@admin_required
@require_POST
def appointment_set_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get('status', '')
    if new_status in Appointment.Status.values:  # не доверяем данным клиента
        appointment.status = new_status
        appointment.save()
        messages.success(request, f'Статус заявки №{appointment.pk} обновлён.')
    else:
        messages.error(request, 'Недопустимый статус.')
    return redirect('admin_panel')