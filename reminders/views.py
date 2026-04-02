import calendar
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.http import JsonResponse
from .models import Reminder, Event, DayNote
from .forms import RegisterForm, ReminderForm, EventForm, DayNoteForm


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


# ── PRZYPOMNIENIA ──────────────────────────────────────────

@login_required
def dashboard_view(request):
    reminders = Reminder.objects.filter(user=request.user)

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
        result = reminder.complete_and_renew()
        if result and not reminder.is_done:
            messages.success(request, f'Termin przesunięty na {result.due_date}!')
        else:
            messages.success(request, 'Oznaczono jako wykonane!')
        return redirect('dashboard')
    return redirect('dashboard')


# ── KALENDARZ ──────────────────────────────────────────────

def _build_calendar(year, month, events_qs, notes_by_date=None):
    today = date.today()
    notes_by_date = notes_by_date or {}
    first_day = date(year, month, 1)
    start_weekday = first_day.weekday()
    cal_start = first_day - timedelta(days=start_weekday)
    cal_end = cal_start + timedelta(days=41)

    events_by_date = {}
    for e in events_qs:
        for d in e.dates_range():
            if cal_start <= d <= cal_end:
                events_by_date.setdefault(d, []).append(e)

    weeks = []
    current = cal_start
    for _ in range(6):
        week = []
        for _ in range(7):
            day_events = events_by_date.get(current, [])
            day_notes = notes_by_date.get(current, [])

            # Kolor tła - bierze z calendar_bg ustawionego przez użytkownika
            bg = ''
            for n in day_notes:
                if n.calendar_bg:
                    bg = n.calendar_bg
                    break
            for e in day_events:
                if e.calendar_bg:
                    bg = e.calendar_bg
                    break

            week.append({
                'date': current,
                'day': current.day,
                'in_month': current.month == month,
                'is_today': current == today,
                'events': day_events,
                'bg_color': bg,
                'has_notes': bool(day_notes),
            })
            current += timedelta(days=1)
        weeks.append(week)

    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    month_names = [
        '', 'Styczeń', 'Luty', 'Marzec', 'Kwiecień', 'Maj', 'Czerwiec',
        'Lipiec', 'Sierpień', 'Wrzesień', 'Październik', 'Listopad', 'Grudzień',
    ]

    return {
        'weeks': weeks,
        'month_name': month_names[month],
        'year': year,
        'month': month,
        'prev_year': prev_year,
        'prev_month': prev_month,
        'next_year': next_year,
        'next_month': next_month,
    }


@login_required
def calendar_view(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    selected_date_str = request.GET.get('day', '')

    if selected_date_str:
        try:
            parts = selected_date_str.split('-')
            selected_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
        except (ValueError, IndexError):
            selected_date = today
    else:
        selected_date = None

    events = Event.objects.filter(user=request.user)

    # Zbierz notatki dla kalendarza (kolory tła)
    all_notes = DayNote.objects.filter(user=request.user)
    notes_by_date = {}
    for n in all_notes:
        notes_by_date.setdefault(n.date, []).append(n)

    cal = _build_calendar(year, month, events, notes_by_date)

    # Notatki i wydarzenia wybranego dnia
    day_notes = []
    day_events = []
    if selected_date:
        day_notes = DayNote.objects.filter(user=request.user, date=selected_date)
        day_events = Event.objects.filter(user=request.user)
        day_events = [e for e in day_events if selected_date in e.dates_range()]

    # Statystyki punktów per przedmiot
    quiz_notes = DayNote.objects.filter(user=request.user, has_quiz=True, quiz_score__isnull=False)
    subject_stats = {}
    for n in quiz_notes:
        label = n.get_subject_display()
        if label not in subject_stats:
            subject_stats[label] = {'total_score': 0, 'total_max': 0, 'count': 0, 'scores': []}
        s = subject_stats[label]
        s['total_score'] += float(n.quiz_score)
        s['total_max'] += float(n.quiz_max) if n.quiz_max else 0
        s['count'] += 1
        s['scores'].append({'score': float(n.quiz_score), 'max': float(n.quiz_max) if n.quiz_max else 0, 'date': n.date})
    for label, s in subject_stats.items():
        s['percent'] = round(s['total_score'] / s['total_max'] * 100) if s['total_max'] > 0 else 0

    return render(request, 'reminders/calendar.html', {
        **cal,
        'event_types': Event.TYPE_CHOICES,
        'selected_date': selected_date,
        'day_notes': day_notes,
        'day_events': day_events,
        'subject_stats': subject_stats,
    })


@login_required
def event_add(request):
    initial = {}
    if request.GET.get('date'):
        initial['date'] = request.GET['date']
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            messages.success(request, 'Wydarzenie dodane!')
            return redirect('calendar')
    else:
        form = EventForm(initial=initial)
    return render(request, 'reminders/event_form.html', {'form': form, 'title': 'Dodaj wydarzenie'})


@login_required
def event_edit(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Wydarzenie zaktualizowane!')
            return redirect('calendar')
    else:
        form = EventForm(instance=event)
    return render(request, 'reminders/event_form.html', {'form': form, 'title': 'Edytuj wydarzenie'})


@login_required
def event_delete(request, pk):
    event = get_object_or_404(Event, pk=pk, user=request.user)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Wydarzenie usunięte!')
        return redirect('calendar')
    return render(request, 'reminders/event_confirm_delete.html', {'event': event})


# ── NOTATKI DNIA ───────────────────────────────────────────

@login_required
def note_add(request, date_str):
    try:
        parts = date_str.split('-')
        note_date = date(int(parts[0]), int(parts[1]), int(parts[2]))
    except (ValueError, IndexError):
        return redirect('calendar')

    if request.method == 'POST':
        form = DayNoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.date = note_date
            note.save()
            messages.success(request, 'Notatka dodana!')
            return redirect(f'/kalendarz/?year={note_date.year}&month={note_date.month}&day={date_str}')
    else:
        form = DayNoteForm()
    return render(request, 'reminders/note_form.html', {
        'form': form,
        'title': f'Dodaj zajęcia - {note_date.strftime("%d.%m.%Y")}',
        'note_date': note_date,
    })


@login_required
def note_edit(request, pk):
    note = get_object_or_404(DayNote, pk=pk, user=request.user)
    if request.method == 'POST':
        form = DayNoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notatka zaktualizowana!')
            ds = note.date.strftime('%Y-%m-%d')
            return redirect(f'/kalendarz/?year={note.date.year}&month={note.date.month}&day={ds}')
    else:
        form = DayNoteForm(instance=note)
    return render(request, 'reminders/note_form.html', {
        'form': form,
        'title': f'Edytuj - {note.subject}',
        'note_date': note.date,
    })


@login_required
def note_delete(request, pk):
    note = get_object_or_404(DayNote, pk=pk, user=request.user)
    note_date = note.date
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Notatka usunięta!')
        ds = note_date.strftime('%Y-%m-%d')
        return redirect(f'/kalendarz/?year={note_date.year}&month={note_date.month}&day={ds}')
    return render(request, 'reminders/note_confirm_delete.html', {'note': note})


@login_required
def note_toggle(request, pk):
    note = get_object_or_404(DayNote, pk=pk, user=request.user)
    if request.method == 'POST':
        note.is_done = not note.is_done
        note.save()
    ds = note.date.strftime('%Y-%m-%d')
    return redirect(f'/kalendarz/?year={note.date.year}&month={note.date.month}&day={ds}')


@login_required
def calendar_api(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    events = Event.objects.filter(user=request.user)
    if start:
        events = events.filter(date__gte=start)
    if end:
        events = events.filter(date__lte=end)
    result = []
    for e in events:
        result.append({
            'id': e.pk,
            'title': e.title,
            'date': e.date.isoformat(),
            'end_date': e.end_date.isoformat() if e.end_date else None,
            'type': e.get_event_type_display(),
            'color': e.color,
            'icon': e.icon,
            'time': e.time.strftime('%H:%M') if e.time else None,
        })
    return JsonResponse(result, safe=False)


# ── PROFIL ──────────────────────────────────────────────────

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
        'events': Event.objects.filter(user=request.user, date__gte=date.today()).count(),
    }
    return render(request, 'reminders/profile.html', {'form': form, 'stats': stats})
