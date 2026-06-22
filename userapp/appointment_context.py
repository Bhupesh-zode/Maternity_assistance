"""Load and format user appointments for the pregnancy assistant."""

from django.utils import timezone

from userapp.models import Appointment

ACTIVE_STATUSES = (
    Appointment.STATUS_PENDING,
    Appointment.STATUS_CONFIRMED,
    Appointment.STATUS_RESCHEDULED,
)

TIME_LABELS = dict(Appointment.TIME_SLOTS)


def _time_label(time_value):
    return TIME_LABELS.get(time_value, time_value or '')


def _status_label(status):
    return dict(Appointment.STATUS_CHOICES).get(status, status)


def get_user_appointments(user_sno):
    if user_sno is None:
        return []
    return list(
        Appointment.objects.filter(user_sno=user_sno).order_by('-created_at')[:20]
    )


def _upcoming_appointments(appointments, today):
    rows = []
    for appt in appointments:
        if appt.status not in ACTIVE_STATUSES:
            continue
        if appt.display_date < today:
            continue
        rows.append(appt)
    rows.sort(key=lambda row: (row.display_date, row.display_time or ''))
    return rows


def _recent_completed(appointments, limit=3):
    rows = [
        appt for appt in appointments
        if appt.status == Appointment.STATUS_COMPLETED
    ]
    rows.sort(key=lambda row: (row.display_date, row.display_time or ''), reverse=True)
    return rows[:limit]


def _format_appointment_line(appt):
    date_str = appt.display_date.strftime('%a, %b %d, %Y')
    time_str = _time_label(appt.display_time)
    line = f'• {date_str} at {time_str} — {_status_label(appt.status)}'
    if appt.admin_notes and appt.status in (
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_RESCHEDULED,
    ):
        line += f' (admin note: {appt.admin_notes.strip()})'
    elif appt.notes and appt.status == Appointment.STATUS_PENDING:
        line += f' (your note: {appt.notes.strip()[:80]})'
    return line


def format_appointments_summary(user_sno):
    """Plain-text summary for rule-based chat replies."""
    appointments = get_user_appointments(user_sno)
    if not appointments:
        return ''

    today = timezone.localdate()
    upcoming = _upcoming_appointments(appointments, today)
    recent = _recent_completed(appointments)

    parts = []
    if upcoming:
        parts.append('Your upcoming appointments:')
        parts.extend(_format_appointment_line(appt) for appt in upcoming)
    else:
        parts.append('You have no upcoming appointments scheduled in the app.')

    if recent:
        parts.append('')
        parts.append('Recently completed:')
        parts.extend(_format_appointment_line(appt) for appt in recent)

    parts.append('')
    parts.append(
        'Open Appointments in the menu to book a new slot or cancel a pending request.'
    )
    return '\n'.join(parts)


def format_appointments_context_for_ai(user_sno):
    """Compact context block appended to the Gemini system prompt."""
    appointments = get_user_appointments(user_sno)
    if not appointments:
        return (
            '\nApp context (appointments): This user has no appointment records yet. '
            'If they ask about booking, tell them to use Appointments in the menu.\n'
        )

    today = timezone.localdate()
    upcoming = _upcoming_appointments(appointments, today)
    recent = _recent_completed(appointments, limit=2)

    lines = ['\nApp context (this user\'s appointments — use when they ask about schedule):']
    if upcoming:
        lines.append('Upcoming / active:')
        lines.extend(_format_appointment_line(appt) for appt in upcoming)
    else:
        lines.append('Upcoming / active: none on or after today.')

    if recent:
        lines.append('Recent completed:')
        lines.extend(_format_appointment_line(appt) for appt in recent)

    lines.append(
        'If they ask to book, change, or cancel, explain status and point them to '
        'Appointments in the app (pending requests can be cancelled there). '
        'Do not invent appointments not listed above.'
    )
    return '\n'.join(lines) + '\n'
