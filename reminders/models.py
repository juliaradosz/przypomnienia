from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class Reminder(models.Model):
    CATEGORY_CHOICES = [
        ('dowod', 'Dowód osobisty'),
        ('paszport', 'Paszport'),
        ('prawo_jazdy', 'Prawo jazdy'),
        ('ubezpieczenie', 'Ubezpieczenie'),
        ('przeglad', 'Przegląd samochodu'),
        ('smieci', 'Wywóz śmieci'),
        ('rachunki', 'Rachunki / opłaty'),
        ('lekarz', 'Wizyta u lekarza'),
        ('studia', 'Studia / egzamin'),
        ('inne', 'Inne'),
    ]

    CATEGORY_ICONS = {
        'dowod': 'bi-person-badge',
        'paszport': 'bi-globe-europe-africa',
        'prawo_jazdy': 'bi-car-front',
        'ubezpieczenie': 'bi-shield-check',
        'przeglad': 'bi-tools',
        'smieci': 'bi-trash3',
        'rachunki': 'bi-wallet2',
        'lekarz': 'bi-heart-pulse',
        'studia': 'bi-mortarboard',
        'inne': 'bi-bookmark',
    }

    CATEGORY_COLORS = {
        'dowod': '#6366f1',
        'paszport': '#8b5cf6',
        'prawo_jazdy': '#3b82f6',
        'ubezpieczenie': '#06b6d4',
        'przeglad': '#f59e0b',
        'smieci': '#22c55e',
        'rachunki': '#ef4444',
        'lekarz': '#ec4899',
        'studia': '#f472b6',
        'inne': '#6b7280',
    }

    REPEAT_CHOICES = [
        ('none', 'Bez powtarzania'),
        ('weekly', 'Co tydzień'),
        ('biweekly', 'Co 2 tygodnie'),
        ('monthly', 'Co miesiąc'),
        ('quarterly', 'Co kwartał'),
        ('yearly', 'Co rok'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField('Tytuł', max_length=200)
    category = models.CharField('Kategoria', max_length=30, choices=CATEGORY_CHOICES, default='inne')
    description = models.TextField('Opis', blank=True)
    due_date = models.DateField('Termin')
    remind_days_before = models.PositiveIntegerField('Przypomnij dni przed terminem', default=7)
    repeat = models.CharField('Powtarzanie', max_length=20, choices=REPEAT_CHOICES, default='none')
    is_done = models.BooleanField('Wykonane', default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Przypomnienie'
        verbose_name_plural = 'Przypomnienia'

    def __str__(self):
        return f'{self.title} ({self.get_category_display()}) - {self.due_date}'

    @property
    def icon(self):
        return self.CATEGORY_ICONS.get(self.category, 'bi-bookmark')

    @property
    def color(self):
        return self.CATEGORY_COLORS.get(self.category, '#6b7280')

    @property
    def is_urgent(self):
        today = timezone.now().date()
        delta = (self.due_date - today).days
        return 0 <= delta <= self.remind_days_before and not self.is_done

    @property
    def is_expired(self):
        return self.due_date < timezone.now().date() and not self.is_done

    @property
    def days_left(self):
        return (self.due_date - timezone.now().date()).days

    @property
    def status(self):
        if self.is_done:
            return 'done'
        if self.is_expired:
            return 'expired'
        if self.is_urgent:
            return 'urgent'
        return 'ok'

    def complete_and_renew(self):
        """Oznacz jako wykonane, lub przesuń datę jeśli cykliczne."""
        if self.repeat == 'none':
            self.is_done = True
            self.save()
            return None

        delta_map = {
            'weekly': datetime.timedelta(weeks=1),
            'biweekly': datetime.timedelta(weeks=2),
            'monthly': datetime.timedelta(days=30),
            'quarterly': datetime.timedelta(days=91),
            'yearly': datetime.timedelta(days=365),
        }
        delta = delta_map.get(self.repeat)
        if delta:
            new_date = self.due_date + delta
            while new_date <= timezone.now().date():
                new_date += delta
            self.due_date = new_date
            self.save()
            return self
        return None


class Event(models.Model):
    TYPE_CHOICES = [
        ('wolne', 'Dzień wolny'),
        ('egzamin', 'Egzamin'),
        ('kolokwium', 'Kolokwium'),
        ('projekt', 'Oddanie projektu'),
        ('spotkanie', 'Spotkanie'),
        ('wyjazd', 'Wyjazd / urlop'),
        ('impreza', 'Impreza / wydarzenie'),
        ('inne', 'Inne'),
    ]

    TYPE_ICONS = {
        'wolne': 'bi-sun',
        'egzamin': 'bi-mortarboard',
        'kolokwium': 'bi-pencil-square',
        'projekt': 'bi-folder-check',
        'spotkanie': 'bi-people',
        'wyjazd': 'bi-airplane',
        'impreza': 'bi-star',
        'inne': 'bi-calendar-event',
    }

    TYPE_COLORS = {
        'wolne': '#22c55e',
        'egzamin': '#ef4444',
        'kolokwium': '#f59e0b',
        'projekt': '#8b5cf6',
        'spotkanie': '#3b82f6',
        'wyjazd': '#06b6d4',
        'impreza': '#ec4899',
        'inne': '#6b7280',
    }

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField('Tytuł', max_length=200)
    event_type = models.CharField('Typ', max_length=30, choices=TYPE_CHOICES, default='inne')
    description = models.TextField('Opis', blank=True)
    date = models.DateField('Data')
    end_date = models.DateField('Data końcowa', blank=True, null=True,
                                help_text='Zostaw puste jeśli jednodniowe')
    all_day = models.BooleanField('Cały dzień', default=True)
    time = models.TimeField('Godzina', blank=True, null=True,
                            help_text='Opcjonalnie, jeśli nie cały dzień')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']
        verbose_name = 'Wydarzenie'
        verbose_name_plural = 'Wydarzenia'

    def __str__(self):
        return f'{self.title} ({self.get_event_type_display()}) - {self.date}'

    @property
    def icon(self):
        return self.TYPE_ICONS.get(self.event_type, 'bi-calendar-event')

    @property
    def color(self):
        return self.TYPE_COLORS.get(self.event_type, '#6b7280')

    @property
    def is_multiday(self):
        return self.end_date and self.end_date > self.date

    def dates_range(self):
        """Zwraca listę wszystkich dat wydarzenia."""
        if not self.end_date or self.end_date <= self.date:
            return [self.date]
        days = []
        current = self.date
        while current <= self.end_date:
            days.append(current)
            current += datetime.timedelta(days=1)
        return days
