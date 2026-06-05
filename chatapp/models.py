import os
import uuid

from django.db import models


def support_attachment_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f'{uuid.uuid4().hex}{ext}'
    return f'support_messages/{instance.user_sno}/{safe_name}'


class ChatMessage(models.Model):
    ROLE_USER = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES = [
        (ROLE_USER, 'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    ]

    user_sno = models.IntegerField(db_index=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.role} @ {self.created_at:%Y-%m-%d %H:%M}'


class SupportMessage(models.Model):
    SENDER_USER = 'user'
    SENDER_ADMIN = 'admin'
    SENDER_CHOICES = [
        (SENDER_USER, 'User'),
        (SENDER_ADMIN, 'Admin'),
    ]

    user_sno = models.IntegerField(db_index=True)
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to=support_attachment_path, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'support_messages'
        ordering = ['created_at']

    IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

    @property
    def has_attachment(self):
        return bool(self.attachment)

    @property
    def is_image_attachment(self):
        if not self.attachment:
            return False
        ext = os.path.splitext(self.attachment.name)[1].lower()
        return ext in self.IMAGE_EXTENSIONS

    @property
    def attachment_basename(self):
        if not self.attachment:
            return ''
        return os.path.basename(self.attachment.name)

    def __str__(self):
        return f'{self.sender} (user {self.user_sno}) @ {self.created_at:%Y-%m-%d %H:%M}'
