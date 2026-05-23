from django.contrib import admin
from chatapp.models import ChatMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)
