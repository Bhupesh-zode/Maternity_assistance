from django.contrib import admin
from chatapp.models import ChatMessage, SupportMessage


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('content',)


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_sno', 'sender', 'is_read', 'created_at', 'has_attachment')
    list_filter = ('sender', 'is_read', 'created_at')
    search_fields = ('content',)

    @admin.display(boolean=True, description='Attachment')
    def has_attachment(self, obj):
        return obj.has_attachment
