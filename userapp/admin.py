from django.contrib import admin

from userapp.models import Appointment, PredictionHistory, UserNotification, UserPrediction


@admin.register(UserPrediction)
class UserPredictionAdmin(admin.ModelAdmin):
    list_display = ('user_sno', 'predicted_mode', 'updated_at')
    search_fields = ('user_sno', 'predicted_mode')


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'predicted_mode', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_sno', 'predicted_mode')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'preferred_date', 'preferred_time', 'status', 'created_at')
    list_filter = ('status', 'preferred_date')
    search_fields = ('user_sno', 'notes')


@admin.register(UserNotification)
class UserNotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'kind', 'title', 'is_read', 'created_at')
    list_filter = ('kind', 'is_read')
