from django.db import models

from ..command.models import TimeStampModel


# Create your models here.

class Relatives(TimeStampModel):
    name = models.CharField(null=True, blank=True, max_length=100)
    phone = models.CharField(null=True, blank=True, max_length=100)
    who = models.CharField(null=True, blank=True, max_length=100)

    def __str__(self):
        return f"{self.who}"