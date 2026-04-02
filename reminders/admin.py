from django.contrib import admin
from .models import Reminder


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'due_date', 'user', 'created_at']
    list_filter = ['category', 'due_date']
    search_fields = ['title', 'description']
