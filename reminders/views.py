from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Reminder
from .forms import RegisterForm, ReminderForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Konto zostało utworzone!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'reminders/register.html', {'form': form})


@login_required
def dashboard_view(request):
    reminders = Reminder.objects.filter(user=request.user)
    urgent = [r for r in reminders if r.is_urgent]
    expired = [r for r in reminders if r.is_expired]
    upcoming = [r for r in reminders if not r.is_expired and not r.is_urgent]
    return render(request, 'reminders/dashboard.html', {
        'urgent': urgent,
        'expired': expired,
        'upcoming': upcoming,
    })


@login_required
def reminder_add(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
            messages.success(request, 'Przypomnienie dodane!')
            return redirect('dashboard')
    else:
        form = ReminderForm()
    return render(request, 'reminders/reminder_form.html', {'form': form, 'title': 'Dodaj przypomnienie'})


@login_required
def reminder_edit(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ReminderForm(request.POST, instance=reminder)
        if form.is_valid():
            form.save()
            messages.success(request, 'Przypomnienie zaktualizowane!')
            return redirect('dashboard')
    else:
        form = ReminderForm(instance=reminder)
    return render(request, 'reminders/reminder_form.html', {'form': form, 'title': 'Edytuj przypomnienie'})


@login_required
def reminder_delete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        messages.success(request, 'Przypomnienie usunięte!')
        return redirect('dashboard')
    return render(request, 'reminders/reminder_confirm_delete.html', {'reminder': reminder})
