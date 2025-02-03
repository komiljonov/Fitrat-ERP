from django.db import models

from ..command.models import TimeStampModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


# Create your models here.

class Relatives(TimeStampModel):
    name = models.CharField(null=True, blank=True, max_length=100)
    phone = models.CharField(null=True, blank=True, max_length=100)
    who = models.CharField(null=True, blank=True, max_length=100)

    lid: 'Lid' = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL, null=True, blank=True)
    student: 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True, blank=True)


def __str__(self):
        return f"{self.who}"