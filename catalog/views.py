from django.shortcuts import render

# Create your views here.
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ServiceForm
from .models import Category, Mechanic, Service


def home(request):
    return render(request, 'home.html', {
        'services_count': Service.objects.count(),
        'mechanics_count': Mechanic.objects.count(),
        'latest_services': Service.objects.select_related('category', 'mechanic')[:3],
    })


def service_list(request):
    services = Service.objects.select_related('category', 'mechanic')

    query = request.GET.get('q', '').strip()
    category_raw = request.GET.get('category', '').strip()
    mechanic_raw = request.GET.get('mechanic', '').strip()

    if query:
        services = services.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    active_category = int(category_raw) if category_raw.isdigit() else None
    if active_category:
        services = services.filter(category_id=active_category)

    active_mechanic = None
    if mechanic_raw.isdigit():
        services = services.filter(mechanic_id=int(mechanic_raw))
        active_mechanic = Mechanic.objects.filter(pk=int(mechanic_raw)).first()

    return render(request, 'catalog/service_list.html', {
        'services': services,
        'categories': Category.objects.all(),
        'query': query,
        'active_category': active_category,
        'active_mechanic': active_mechanic,
    })


def service_detail(request, pk):
    service = get_object_or_404(
        Service.objects.select_related('category', 'mechanic'), pk=pk
    )
    related = Service.objects.filter(category=service.category).exclude(pk=service.pk)[:3]
    return render(request, 'catalog/service_detail.html', {
        'service': service,
        'related_services': related,
    })


def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Услуга «{service.title}» добавлена в каталог.')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm()
    return render(request, 'catalog/service_form.html', {
        'form': form, 'title': 'Добавить услугу',
    })


def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, request.FILES, instance=service)
        if form.is_valid():
            form.save()
            messages.success(request, 'Изменения сохранены.')
            return redirect('service_detail', pk=service.pk)
    else:
        form = ServiceForm(instance=service)
    return render(request, 'catalog/service_form.html', {
        'form': form, 'title': 'Редактировать услугу', 'service': service,
    })


def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        title = service.title
        service.delete()
        messages.success(request, f'Услуга «{title}» удалена.')
        return redirect('service_list')
    return render(request, 'catalog/service_confirm_delete.html', {'service': service})


def booking(request):
    return render(request, 'booking.html', {
        'services': Service.objects.select_related('mechanic').order_by('title'),
    })


def contacts(request):
    return render(request, 'contacts.html', {
        'mechanics': Mechanic.objects.all(),
        'services_count': Service.objects.count(),
        'categories_count': Category.objects.count(),
    })


