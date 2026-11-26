from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name', 'email', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    fieldsets = UserAdmin.fieldsets + (
        ('Профиль AutoFix', {'fields': ('full_name', 'phone', 'role')}),
    )