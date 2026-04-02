from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Reminder


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
