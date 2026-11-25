from django.contrib import admin
from django.db.models import Count

from .models import Category, Mechanic, Service


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'services_total')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(total=Count('services'))

    @admin.display(description='Услуг', ordering='total')
    def services_total(self, obj):
        return obj.total


@admin.register(Mechanic)
class MechanicAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'specialization', 'experience')
    search_fields = ('full_name', 'specialization')
    list_filter = ('experience',)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'mechanic', 'price', 'duration_minutes', 'created_at')
    list_filter = ('category', 'mechanic')
    search_fields = ('title', 'description')
    list_select_related = ('category', 'mechanic')
    list_per_page = 20


admin.site.site_header = 'AutoFix — управление автосервисом'
admin.site.site_title = 'AutoFix Admin'
admin.site.index_title = 'Каталог услуг, категории и механики'