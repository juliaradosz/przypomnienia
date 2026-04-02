from django.db import models
from django.contrib.auth.models import User


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
        ('inne', 'Inne'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField('Tytuł', max_length=200)
    category = models.CharField('Kategoria', max_length=30, choices=CATEGORY_CHOICES, default='inne')
    description = models.TextField('Opis', blank=True)
    due_date = models.DateField('Termin')
    remind_days_before = models.PositiveIntegerField('Przypomnij dni przed terminem', default=7)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date']
        verbose_name = 'Przypomnienie'
        verbose_name_plural = 'Przypomnienia'

    def __str__(self):
        return f'{self.title} ({self.get_category_display()}) - {self.due_date}'

    @property
    def is_urgent(self):
        from django.utils import timezone
        today = timezone.now().date()
        delta = (self.due_date - today).days
        return 0 <= delta <= self.remind_days_before

    @property
    def is_expired(self):
        from django.utils import timezone
        return self.due_date < timezone.now().date()

    @property
    def days_left(self):
        from django.utils import timezone
        return (self.due_date - timezone.now().date()).days
