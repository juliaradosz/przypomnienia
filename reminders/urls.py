from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('rejestracja/', views.register_view, name='register'),
    path('logowanie/', auth_views.LoginView.as_view(template_name='reminders/login.html'), name='login'),
    path('wyloguj/', auth_views.LogoutView.as_view(), name='logout'),
    path('profil/', views.profile_view, name='profile'),
    # Przypomnienia
    path('dodaj/', views.reminder_add, name='reminder_add'),
    path('edytuj/<int:pk>/', views.reminder_edit, name='reminder_edit'),
    path('usun/<int:pk>/', views.reminder_delete, name='reminder_delete'),
    path('wykonane/<int:pk>/', views.reminder_complete, name='reminder_complete'),
    # Kalendarz
    path('kalendarz/', views.calendar_view, name='calendar'),
    path('kalendarz/dodaj/', views.event_add, name='event_add'),
    path('kalendarz/edytuj/<int:pk>/', views.event_edit, name='event_edit'),
    path('kalendarz/usun/<int:pk>/', views.event_delete, name='event_delete'),
    path('api/kalendarz/', views.calendar_api, name='calendar_api'),
]
