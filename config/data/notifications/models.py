from django.contrib.auth import get_user_model
from django.db import models

from ..account.models import CustomUser
from ..command.models import TimeStampModel


class Notification(TimeStampModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    come_from = models.TextField(null=True,blank=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} | {self.comment} | {self.come_from} {self.is_read}"


class Complaint(TimeStampModel):
    user : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL, null=True,blank=True)

    text = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"{self.user}"
