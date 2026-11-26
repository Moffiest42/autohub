from django.urls import path

from . import views

urlpatterns = [
    path('booking/', views.booking, name='booking'),
    path('my/', views.my_appointments, name='my_appointments'),
    path('my/<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('my/<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('manage/', views.admin_panel, name='admin_panel'),
    path('manage/<int:pk>/status/', views.appointment_set_status, name='appointment_set_status'),
]