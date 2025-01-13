from django.db import models

from ...command.models import TimeStampModel

class MarketingChannel(TimeStampModel):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.name