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
