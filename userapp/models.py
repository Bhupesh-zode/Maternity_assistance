from django.db import models


class UserPrediction(models.Model):
    """Latest childbirth prediction per user (updated on each Predict submit)."""

    user_sno = models.IntegerField(unique=True, db_index=True)
    predicted_mode = models.CharField(max_length=120)
    summary = models.CharField(max_length=255, blank=True)
    form_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_predictions'
        ordering = ['-updated_at']

    def __str__(self):
        return f'user {self.user_sno}: {self.predicted_mode}'


class PredictionHistory(models.Model):
    """Every Predict run, kept for history (latest still in UserPrediction)."""

    user_sno = models.IntegerField(db_index=True)
    predicted_mode = models.CharField(max_length=120)
    summary = models.CharField(max_length=255, blank=True)
    form_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'prediction_history'
        ordering = ['-created_at']

    def __str__(self):
        return f'user {self.user_sno}: {self.predicted_mode} @ {self.created_at:%Y-%m-%d}'


class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_RESCHEDULED = 'rescheduled'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_RESCHEDULED, 'Rescheduled'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    TIME_SLOTS = [
        ('09:00', '09:00 AM'),
        ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'),
        ('14:00', '02:00 PM'),
        ('15:00', '03:00 PM'),
        ('16:00', '04:00 PM'),
    ]

    user_sno = models.IntegerField(db_index=True)
    preferred_date = models.DateField()
    preferred_time = models.CharField(max_length=5, choices=TIME_SLOTS)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    confirmed_date = models.DateField(null=True, blank=True)
    confirmed_time = models.CharField(max_length=5, choices=TIME_SLOTS, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'appointments'
        ordering = ['-created_at']

    @property
    def display_date(self):
        if self.status in (self.STATUS_CONFIRMED, self.STATUS_RESCHEDULED) and self.confirmed_date:
            return self.confirmed_date
        return self.preferred_date

    @property
    def display_time(self):
        if self.status in (self.STATUS_CONFIRMED, self.STATUS_RESCHEDULED) and self.confirmed_time:
            return self.confirmed_time
        return self.preferred_time

    def __str__(self):
        return f'user {self.user_sno} · {self.display_date} · {self.status}'


class UserNotification(models.Model):
    KIND_MESSAGE = 'message'
    KIND_APPOINTMENT = 'appointment'
    KIND_PREDICTION = 'prediction'
    KIND_CHOICES = [
        (KIND_MESSAGE, 'Message'),
        (KIND_APPOINTMENT, 'Appointment'),
        (KIND_PREDICTION, 'Prediction'),
    ]

    user_sno = models.IntegerField(db_index=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES)
    title = models.CharField(max_length=120)
    body = models.CharField(max_length=255, blank=True)
    link = models.CharField(max_length=120, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} → user {self.user_sno}'
