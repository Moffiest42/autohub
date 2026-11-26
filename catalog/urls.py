from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.service_create, name='service_create'),
    path('services/<int:pk>/', views.service_detail, name='service_detail'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('contacts/', views.contacts, name='contacts'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
]