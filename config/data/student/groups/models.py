
from django.db import models


from django.utils.timezone import now

from ...command.models import TimeStampModel

from ...account.models import CustomUser

class Group(TimeStampModel):
    name = models.CharField(max_length=100)

    teacher : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT)

    price_type = models.CharField(choices=[
        ('DAILY', 'Daily payment'),
        ('MONTHLY', 'Monthly payment'),
    ],
        default='DAILY',
        max_length=100)
    price = models.FloatField(default=0, null=True, blank=True)
    scheduled_day_type = models.CharField(choices=[
        ('EVERYDAY', 'Every day'),
        ('ODD', 'Toq kunlar'),
        ('EVEN', 'Juft kunlar'),
    ],
        default='EVERYDAY',
        max_length=100)

    started_at = models.DateTimeField(default=now)  # Use timezone-aware default
    ended_at = models.DateTimeField(default=now)
    def __str__(self):
        return f"{self.name} - {self.price_type} - {self.scheduled_day_type}"


