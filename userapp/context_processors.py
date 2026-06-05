from chatapp.models import SupportMessage
from userapp.models import Appointment, UserNotification


def user_portal(request):
    sno = request.session.get('sno')
    if not sno:
        return {}
    return {
        'unread_message_count': SupportMessage.objects.filter(
            user_sno=sno,
            sender=SupportMessage.SENDER_ADMIN,
            is_read=False,
        ).count(),
        'unread_notification_count': UserNotification.objects.filter(
            user_sno=sno,
            is_read=False,
        ).count(),
        'alert_preview_notifications': UserNotification.objects.filter(
            user_sno=sno,
        ).order_by('-created_at')[:5],
    }


def admin_portal(request):
    if not request.session.get('admin_logged_in'):
        return {}
    return {
        'admin_unread_message_count': SupportMessage.objects.filter(
            sender=SupportMessage.SENDER_USER,
            is_read=False,
        ).count(),
        'admin_pending_appointment_count': Appointment.objects.filter(
            status=Appointment.STATUS_PENDING,
        ).count(),
    }
