from django.contrib import admin
from .models import Reminder, Event, DayNote


@admin.register(Reminder)
class ReminderAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'due_date', 'user', 'created_at']
    list_filter = ['category', 'due_date']
    search_fields = ['title', 'description']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'date', 'end_date', 'user', 'created_at']
    list_filter = ['event_type', 'date']
    search_fields = ['title', 'description']


@admin.register(DayNote)
class DayNoteAdmin(admin.ModelAdmin):
    list_display = ['subject', 'date', 'has_quiz', 'quiz_score', 'is_done', 'user']
    list_filter = ['date', 'has_quiz', 'is_done']
    search_fields = ['subject', 'note', 'homework']
