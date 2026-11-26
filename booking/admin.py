from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'date', 'time', 'status', 'created_at')
    list_filter = ('status', 'date')
    search_fields = ('user__username', 'user__full_name', 'car_info')
    list_select_related = ('user', 'service')