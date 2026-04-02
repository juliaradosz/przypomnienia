from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from .models import Reminder
from .forms import RegisterForm, ReminderForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Konto zostało utworzone! Witaj!')
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'reminders/register.html', {'form': form})


@login_required
def dashboard_view(request):
    reminders = Reminder.objects.filter(user=request.user)

    # Filtrowanie
    category = request.GET.get('category', '')
    search = request.GET.get('search', '')
    show = request.GET.get('show', 'active')

    if category:
        reminders = reminders.filter(category=category)
    if search:
        reminders = reminders.filter(title__icontains=search)

    if show == 'done':
        reminders = reminders.filter(is_done=True)
        urgent = []
        expired = []
        upcoming = list(reminders)
    elif show == 'all':
        urgent = [r for r in reminders if r.is_urgent]
        expired = [r for r in reminders if r.is_expired]
        upcoming = [r for r in reminders if not r.is_expired and not r.is_urgent]
    else:
        reminders = reminders.filter(is_done=False)
        urgent = [r for r in reminders if r.is_urgent]
        expired = [r for r in reminders if r.is_expired]
        upcoming = [r for r in reminders if not r.is_expired and not r.is_urgent]

    # Statystyki
    all_reminders = Reminder.objects.filter(user=request.user, is_done=False)
    stats = {
        'total': all_reminders.count(),
        'urgent': sum(1 for r in all_reminders if r.is_urgent),
        'expired': sum(1 for r in all_reminders if r.is_expired),
        'done': Reminder.objects.filter(user=request.user, is_done=True).count(),
    }

    return render(request, 'reminders/dashboard.html', {
        'urgent': urgent,
        'expired': expired,
        'upcoming': upcoming,
        'stats': stats,
        'categories': Reminder.CATEGORY_CHOICES,
        'current_category': category,
        'current_search': search,
        'current_show': show,
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


@login_required
def reminder_complete(request, pk):
    reminder = get_object_or_404(Reminder, pk=pk, user=request.user)
    if request.method == 'POST':
        new_reminder = reminder.complete_and_renew()
        if new_reminder:
            messages.success(request, f'Oznaczono jako wykonane! Następne przypomnienie: {new_reminder.due_date}')
        else:
            messages.success(request, 'Oznaczono jako wykonane!')
        return redirect('dashboard')
    return redirect('dashboard')


@login_required
def profile_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Hasło zostało zmienione!')
            return redirect('profile')
    else:
        form = PasswordChangeForm(request.user)

    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    stats = {
        'total': Reminder.objects.filter(user=request.user, is_done=False).count(),
        'done': Reminder.objects.filter(user=request.user, is_done=True).count(),
    }
    return render(request, 'reminders/profile.html', {'form': form, 'stats': stats})
