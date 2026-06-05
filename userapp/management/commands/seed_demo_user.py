"""Seed realistic demo data for a user account (college presentation)."""

from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from chatapp.models import ChatMessage, SupportMessage
from mainapp.models import mainModel
from userapp.models import Appointment, PredictionHistory, UserNotification, UserPrediction

DEMO_EMAIL = 'bhupeshzode9@gmail.com'

SAMPLE_FORM = {
    'age': '28',
    'BMI': '24.5',
    'Weight': '68',
    'Height': '165',
    'parity': '1',
    'Gestational': '32',
    'Weight_increased_during': '9',
    'Number_of_previous_Cesarean': '0',
    'Complications': ' f                  ',
    'Robson': ' group 3     ',
    'art': ' FIV     ',
    'Amniocentesis': ' f                     ',
    'EPISITOMY': 'F',
    'Previous': ' f                   ',
    'Obstetric': ' f                    ',
    'Comorbidity': ' f                ',
    'Start_of_Antenatal_Care': '1º trimester',
    'ArT': ' f       ',
    'Amniotic_Liquid': ' clear        ',
    'Repeated_Miscarriages': 'f',
    'Cardiotocography': 'continuous',
    'Maternal_Education': 'university',
}

PREDICTION_RUNS = [
    ('Vaginal birth', 5, 12),
    ('Cesarean section', 4, 8),
    ('Vaginal birth', 3, 22),
    ('Vaginal birth', 2, 5),
    ('Cesarean section', 1, 18),
    ('Vaginal birth', 1, 28),
    ('Vaginal birth', 0, 10),
    ('Cesarean section', 0, 3),
]


def _month_dt(months_ago, day=15, hour=10):
    now = timezone.now()
    year, month = now.year, now.month - months_ago
    while month < 1:
        month += 12
        year -= 1
    return timezone.make_aware(datetime(year, month, min(day, 28), hour, 30))


class Command(BaseCommand):
    help = f'Seed demo predictions, appointments, chat, and alerts for {DEMO_EMAIL}'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            default=DEMO_EMAIL,
            help='User email to seed (default: demo account)',
        )

    def handle(self, *args, **options):
        email = options['email'].strip().lower()
        try:
            user = mainModel.objects.get(email__iexact=email)
        except mainModel.DoesNotExist as exc:
            raise CommandError(f'No user found with email: {email}') from exc

        if user.status != 'accepted':
            user.status = 'accepted'
            user.save(update_fields=['status'])
            self.stdout.write(self.style.WARNING(f'Account status set to accepted for {email}'))

        sno = user.sno
        self._clear_user_data(sno)
        self._seed_predictions(sno)
        self._seed_appointments(sno)
        self._seed_chat(sno)
        self._seed_support(sno)
        self._seed_notifications(sno)

        self.stdout.write(self.style.SUCCESS(
            f'Demo data seeded for {user.name} ({email}) — sno={sno}'
        ))

    def _clear_user_data(self, sno):
        PredictionHistory.objects.filter(user_sno=sno).delete()
        UserPrediction.objects.filter(user_sno=sno).delete()
        Appointment.objects.filter(user_sno=sno).delete()
        ChatMessage.objects.filter(user_sno=sno).delete()
        SupportMessage.objects.filter(user_sno=sno).delete()
        UserNotification.objects.filter(user_sno=sno).delete()

    def _seed_predictions(self, sno):
        latest = None
        for mode, months_ago, day in PREDICTION_RUNS:
            summary = f'The best way of child birth is {mode}'
            record = PredictionHistory.objects.create(
                user_sno=sno,
                predicted_mode=mode,
                summary=summary,
                form_data={**SAMPLE_FORM, 'Gestational': str(28 + (8 - months_ago))},
            )
            PredictionHistory.objects.filter(pk=record.pk).update(
                created_at=_month_dt(months_ago, day),
            )
            latest = record

        if latest:
            UserPrediction.objects.update_or_create(
                user_sno=sno,
                defaults={
                    'predicted_mode': latest.predicted_mode,
                    'summary': latest.summary,
                    'form_data': latest.form_data,
                },
            )
            UserPrediction.objects.filter(user_sno=sno).update(updated_at=timezone.now())

    def _seed_appointments(self, sno):
        today = timezone.localdate()
        rows = [
            {
                'preferred_date': today + timedelta(days=14),
                'preferred_time': '10:00',
                'notes': 'First trimester check-up and general consultation.',
                'status': Appointment.STATUS_PENDING,
            },
            {
                'preferred_date': today + timedelta(days=7),
                'preferred_time': '14:00',
                'notes': 'Follow-up on recent prediction results.',
                'status': Appointment.STATUS_CONFIRMED,
                'confirmed_date': today + timedelta(days=7),
                'confirmed_time': '14:00',
                'admin_notes': 'Confirmed — please arrive 10 minutes early.',
            },
            {
                'preferred_date': today - timedelta(days=21),
                'preferred_time': '11:00',
                'notes': 'Nutrition and wellness discussion.',
                'status': Appointment.STATUS_COMPLETED,
                'confirmed_date': today - timedelta(days=21),
                'confirmed_time': '11:00',
                'admin_notes': 'Completed successfully.',
            },
            {
                'preferred_date': today - timedelta(days=45),
                'preferred_time': '15:00',
                'notes': 'Rescheduled slot request.',
                'status': Appointment.STATUS_RESCHEDULED,
                'confirmed_date': today - timedelta(days=40),
                'confirmed_time': '16:00',
                'admin_notes': 'Moved to 4 PM as requested.',
            },
        ]
        for row in rows:
            Appointment.objects.create(user_sno=sno, **row)

    def _seed_chat(self, sno):
        pairs = [
            (ChatMessage.ROLE_USER, 'What should I focus on in my second trimester?'),
            (ChatMessage.ROLE_ASSISTANT,
             'In the second trimester, many people feel more energy. Focus on balanced meals, '
             'prenatal vitamins, gentle exercise, and keeping up with scheduled check-ups.'),
            (ChatMessage.ROLE_USER, 'Any red flags I should watch for?'),
            (ChatMessage.ROLE_ASSISTANT,
             'Seek care urgently for heavy bleeding, severe headache with vision changes, '
             'reduced baby movement, or sudden swelling with pain.'),
            (ChatMessage.ROLE_USER, 'How do I use the predict feature?'),
            (ChatMessage.ROLE_ASSISTANT,
             'Open Predict from the menu, fill in the clinical form with your details, '
             'and submit. Your result is saved automatically in Prediction History.'),
        ]
        base = timezone.now() - timedelta(days=10)
        for i, (role, content) in enumerate(pairs):
            msg = ChatMessage.objects.create(user_sno=sno, role=role, content=content)
            ChatMessage.objects.filter(pk=msg.pk).update(
                created_at=base + timedelta(hours=i * 2),
            )

    def _seed_support(self, sno):
        thread = [
            (SupportMessage.SENDER_USER, 'Hello, I had a question about my latest prediction result.', False),
            (SupportMessage.SENDER_ADMIN,
             'Hi! Your latest result is stored in Prediction History. '
             'It is a model recommendation — please discuss it with your clinician.', True),
            (SupportMessage.SENDER_USER, 'Can I book an appointment to discuss this?', False),
            (SupportMessage.SENDER_ADMIN,
             'Yes — use Book Appointment on your dashboard. We will confirm your slot shortly.', False),
        ]
        base = timezone.now() - timedelta(days=5)
        for i, (sender, content, is_read) in enumerate(thread):
            msg = SupportMessage.objects.create(
                user_sno=sno,
                sender=sender,
                content=content,
                is_read=is_read,
            )
            SupportMessage.objects.filter(pk=msg.pk).update(
                created_at=base + timedelta(hours=i * 6),
            )

    def _seed_notifications(self, sno):
        items = [
            (UserNotification.KIND_PREDICTION, 'Prediction saved', 'Your latest result: Cesarean section', '/user-prediction-history', False),
            (UserNotification.KIND_APPOINTMENT, 'Appointment confirmed', 'Your consultation on next week is confirmed.', '/user-appointments', False),
            (UserNotification.KIND_MESSAGE, 'Admin replied', 'New message from the support team.', '/user-messages', True),
            (UserNotification.KIND_PREDICTION, 'Welcome to Maternity Assistance', 'Run your first prediction anytime from the dashboard.', '/user-predict', True),
        ]
        for i, (kind, title, body, link, is_read) in enumerate(items):
            note = UserNotification.objects.create(
                user_sno=sno,
                kind=kind,
                title=title,
                body=body,
                link=link,
                is_read=is_read,
            )
            UserNotification.objects.filter(pk=note.pk).update(
                created_at=timezone.now() - timedelta(days=14 - i * 2),
            )
