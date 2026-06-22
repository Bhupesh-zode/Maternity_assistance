"""Shared helpers for appointment date/time slot availability."""

from datetime import date

from userapp.models import Appointment

ACTIVE_BOOKING_STATUSES = (
    Appointment.STATUS_PENDING,
    Appointment.STATUS_CONFIRMED,
    Appointment.STATUS_RESCHEDULED,
)


def occupied_slot(appointment):
    """Return (date, time) this appointment blocks, or (None, None) if inactive."""
    if appointment.status not in ACTIVE_BOOKING_STATUSES:
        return None, None
    if appointment.status in (
        Appointment.STATUS_CONFIRMED,
        Appointment.STATUS_RESCHEDULED,
    ) and appointment.confirmed_date and appointment.confirmed_time:
        return appointment.confirmed_date, appointment.confirmed_time
    return appointment.preferred_date, appointment.preferred_time


def booked_times_for_date(appt_date, exclude_id=None):
    """Time strings (e.g. '09:00') already taken on appt_date."""
    if not isinstance(appt_date, date):
        return set()

    booked = set()
    qs = Appointment.objects.filter(status__in=ACTIVE_BOOKING_STATUSES)
    if exclude_id is not None:
        qs = qs.exclude(pk=exclude_id)

    for appointment in qs.only(
        'status',
        'preferred_date',
        'preferred_time',
        'confirmed_date',
        'confirmed_time',
    ):
        slot_date, slot_time = occupied_slot(appointment)
        if slot_date == appt_date and slot_time:
            booked.add(slot_time)
    return booked


def is_slot_booked(appt_date, preferred_time, exclude_id=None):
    return preferred_time in booked_times_for_date(appt_date, exclude_id=exclude_id)
