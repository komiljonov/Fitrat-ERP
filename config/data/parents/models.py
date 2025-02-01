from django.db import models
from ..command.models import TimeStampModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

# Create your models here.

class Parent(TimeStampModel):
    student : 'Student' = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True,blank=True)
    lid : "Lid" = models.ForeignKey('new_lid.Lid', on_delete=models.SET_NULL, null=True,blank=True)

    fathers_name = models.CharField(max_length=120)
    fathers_phone = models.CharField(max_length=120)

    mothers_name = models.CharField(max_length=120)
    mothers_phone = models.CharField(max_length=120)

    def __str__(self):
        return f"{self.lid.phone_number if self.lid else self.student.phone}"

