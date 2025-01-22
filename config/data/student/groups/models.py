from django.db import models

from dateutil.utils import today
from django.utils.timezone import now

from ..course.models import Course
from ..subject.models import *
from ...account.models import CustomUser


class Room(TimeStampModel):
    room_number = models.CharField(max_length=100, unique=True)
    room_filling = models.FloatField(default=10, null=True, blank=True)

    def __str__(self):
        return self.room_number

class Day(TimeStampModel):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Group(TimeStampModel):
    name = models.CharField(max_length=100)

    course : 'Course' = models.ForeignKey('course.Course', on_delete=models.CASCADE)

    level : 'Level' = models.ForeignKey('subject.Level', on_delete=models.CASCADE)

    teacher : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.PROTECT)

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
        ],
        default='INACTIVE',
        max_length=100,
    )

    room_number : 'Room' = models.ForeignKey('groups.Room', on_delete=models.CASCADE)

    price_type = models.CharField(choices=[
        ('DAILY', 'Daily payment'),
        ('MONTHLY', 'Monthly payment'),
    ],
        default='DAILY',
        max_length=100)
    price = models.FloatField(default=0, null=True, blank=True)

    scheduled_day_type : 'Day' = models.ManyToManyField('groups.Day')  # Correct Many-to-ManyField definition

    group_type = models.CharField(max_length=100,null=True, blank=True)

    started_at = models.TimeField(default=now)  # Use timezone-aware default
    ended_at = models.TimeField(default=now)

    start_date = models.DateField(default=today())
    finish_date = models.DateField(default=today())

    comment = models.TextField(null=True, blank=True)

    def __str__(self):

        return f"{self.name} - {self.price_type}"






