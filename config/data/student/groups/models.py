from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.timezone import now
from ..student.models import Student
from ...command.models import BaseModel

if TYPE_CHECKING:
    from ..course.models import Course
from ...account.models import CustomUser
from ..subject.models import Level

class Room(BaseModel):
    room_number = models.CharField(max_length=100,)
    room_filling = models.FloatField(default=10, null=True, blank=True)

    def __str__(self):
        return self.room_number


class Day(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

def one_year_from_now():
    return timezone.now() + timedelta(days=365)

class Group(BaseModel):
    name = models.CharField(max_length=100)

    course: 'Course' = models.ForeignKey('course.Course', on_delete=models.CASCADE)

    level : "Level" = models.ForeignKey('subject.Level', on_delete=models.SET_NULL, null=True, blank=True,
                                        related_name='groups_level')

    teacher: 'CustomUser' = models.ForeignKey('account.CustomUser',
                                              on_delete=models.SET_NULL, null=True, blank=True,
                                              related_name='teachers_groups')
    secondary_teacher: 'CustomUser' = models.ForeignKey('account.CustomUser',
                                                        on_delete=models.SET_NULL, null=True, blank=True,
                                                        related_name='secondary_teacher')

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ("PENDING", "Pending"),
            ('INACTIVE', 'Inactive'),
        ],
        default='ACTIVE',
        max_length=100,
    )

    room_number: 'Room' = models.ForeignKey('groups.Room', on_delete=models.CASCADE)

    price_type = models.CharField(choices=[
        ('DAILY', 'Daily payment'),
        ('MONTHLY', 'Monthly payment'),
    ],
        default='DAILY',
        max_length=100)
    price = models.FloatField(default=0, null=True, blank=True)

    scheduled_day_type: 'Day' = models.ManyToManyField('groups.Day')  # Correct Many-to-ManyField definition

    is_secondary = models.BooleanField(default=False, help_text='Is there secondary group?')

    started_at = models.TimeField(default=now)
    ended_at = models.TimeField(default=now)

    start_date = models.DateTimeField(default=timezone.now)

    finish_date = models.DateTimeField(default=one_year_from_now)

    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.price_type}"

class GroupSaleStudent(BaseModel):
    group: 'Group' = models.ForeignKey('groups.Group', on_delete=models.CASCADE,related_name='sale_student_group')
    student: "Student" = models.ForeignKey('student.Student', on_delete=models.CASCADE,related_name='sale_student_student')
    amount = models.FloatField(default=0, null=True, blank=True)


class SecondaryGroup(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    group: "Group" = models.ForeignKey('groups.Group', on_delete=models.CASCADE)

    teacher: 'CustomUser' = models.ForeignKey('account.CustomUser',on_delete=models.SET_NULL, null=True, blank=True,)

    scheduled_day_type: 'Day' = models.ManyToManyField('groups.Day', related_name='secondary_scheduled_day_type')

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ("PENDING", "Pending"),
            ('INACTIVE', 'Inactive'),
        ],
        default='ACTIVE',
        max_length=100,
    )

    started_at = models.TimeField(default=now)  # Use timezone-aware default
    ended_at = models.TimeField(default=now)

    start_date = models.DateTimeField(default=timezone.now)
    finish_date = models.DateTimeField(default=timezone.now)

    comment = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.name



