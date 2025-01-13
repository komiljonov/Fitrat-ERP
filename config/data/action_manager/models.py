from django.db import models
from django.contrib.auth import get_user_model

from ..command.models import TimeStampModel

User = get_user_model()


class ActionLogCustom(TimeStampModel):
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('READ', 'Read'),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="action_logs")
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    endpoint = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    request_data = models.JSONField(null=True, blank=True)
    response_data = models.JSONField(null=True, blank=True)
    status_code = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} by {self.user} on {self.endpoint} at {self.timestamp}"
