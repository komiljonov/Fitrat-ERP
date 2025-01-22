from django.db import models
from ...command.models import TimeStampModel
from ...student.subject.models import Subject


# Create your models here.
class Course(TimeStampModel):
    name = models.CharField(max_length=100)

    subject : Subject = models.ForeignKey('subject.Subject', on_delete=models.CASCADE)


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