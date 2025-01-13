from django.contrib.auth import get_user_model
from django.db import models

from ..command.models import TimeStampModel

User = get_user_model()

class Notification(TimeStampModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    come_from = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"{self.user} | {self.comment} | {self.come_from}"