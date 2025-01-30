from django.db import models

from data.student.subject.models import Theme
from ...command.models import TimeStampModel
from ...student.subject.models import Subject
from ..subject.models import *

# Create your models here.
class Course(TimeStampModel):
    name = models.CharField(max_length=100)

    subject : Subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)
    level: 'Level' = models.ForeignKey('subject.Level', on_delete=models.CASCADE)
    lessons_number = models.CharField(max_length=100,null=True, blank=True,help_text="Number of lessons")

    theme : 'Theme' = models.ManyToManyField('subject.Theme', related_name='courses')

    status = models.CharField(
        choices=[
            ('ACTIVE', 'Active'),
            ('INACTIVE', 'Inactive'),
        ],
        default='INACTIVE',
        max_length=100,
    )

    def __str__(self):
        return f"{self.name} {self.subject} {self.status}"