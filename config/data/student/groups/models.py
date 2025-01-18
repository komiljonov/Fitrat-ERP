from dateutil.utils import today
from django.utils.timezone import now

from ..subject.models import *
from ...account.models import CustomUser


class Group(TimeStampModel):
    name = models.CharField(max_length=100)

    subject : Subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)

    level : Level = models.ForeignKey('subject.Level', on_delete=models.CASCADE)

    teacher : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT)

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
        ],
        default='INACTIVE',
        max_length=100,
    )

    room_number = models.CharField(default='10', max_length=100)

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

    group_type = models.CharField(max_length=100,null=True, blank=True)

    started_at = models.DateTimeField(default=now)  # Use timezone-aware default
    ended_at = models.DateTimeField(default=now)

    start_date = models.DateField(default=today())
    finish_date = models.DateField(default=today())

    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.price_type} - {self.scheduled_day_type}"






