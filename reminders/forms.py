from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reminder, Event, DayNote


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'


class ReminderForm(forms.ModelForm):
    due_date = forms.DateField(
        label='Termin',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )

    class Meta:
        model = Reminder
        fields = ['title', 'category', 'description', 'due_date', 'remind_days_before', 'repeat']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Wymiana dowodu osobistego'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcjonalny opis...'}),
            'remind_days_before': forms.NumberInput(attrs={'class': 'form-control'}),
            'repeat': forms.Select(attrs={'class': 'form-select'}),
        }


class ColorPickerWidget(forms.RadioSelect):
    template_name = 'reminders/widgets/color_picker.html'


class EventForm(forms.ModelForm):
    date = forms.DateField(
        label='Data',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    end_date = forms.DateField(
        label='Data końcowa',
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
    )
    time = forms.TimeField(
        label='Godzina',
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
    )

    class Meta:
        model = Event
        fields = ['title', 'event_type', 'description', 'date', 'end_date', 'all_day', 'time', 'calendar_bg']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Np. Egzamin z matematyki'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Opcjonalny opis...'}),
            'all_day': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendar_bg': ColorPickerWidget(choices=Event.BG_COLOR_CHOICES),
        }


class DayNoteForm(forms.ModelForm):
    class Meta:
        model = DayNote
        fields = ['subject', 'note', 'has_quiz', 'quiz_score', 'quiz_max', 'homework', 'is_done', 'calendar_bg']
        widgets = {
            'subject': forms.Select(attrs={'class': 'form-select'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Notatki z zajęć...'}),
            'has_quiz': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'quiz_score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'step': '0.5'}),
            'quiz_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '10', 'step': '0.5'}),
            'homework': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Zadanie domowe / do przygotowania...'}),
            'is_done': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'calendar_bg': ColorPickerWidget(choices=Event.BG_COLOR_CHOICES),
        }
