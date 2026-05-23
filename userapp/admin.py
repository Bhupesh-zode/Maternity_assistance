from django.contrib import admin

from userapp.models import UserPrediction


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ('user_sno', 'predicted_mode', 'updated_at')
    search_fields = ('user_sno', 'predicted_mode')
