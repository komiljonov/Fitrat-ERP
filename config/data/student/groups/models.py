from typing import TYPE_CHECKING
from django.db import models
from ...command.models import TimeStampModel

if TYPE_CHECKING:
    from ..student.models import Student


class Group(TimeStampModel):
    name = models.CharField(max_length=100)

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
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.price_type} - {self.scheduled_day_type}"


class StudentGroup(TimeStampModel):
    student: "Student" = models.ForeignKey("student.Student", on_delete=models.CASCADE,
                                           related_name="students_group")
    group: "Group" = models.ForeignKey("groups.Group", on_delete=models.CASCADE,
                                       related_name="student_groups")

    student_status = models.CharField(
        choices=[
            ('ACTIVE', 'ACTIVE'),
            ('INACTIVE', 'INACTIVE'),
        ],
        default="ACTIVE",
        max_length=100,
    )

    student: models.QuerySet["Student"]
    group: models.QuerySet["Group"]

    def __str__(self):
        return f"{self.student} | {self.group} | {self.student_status}"
