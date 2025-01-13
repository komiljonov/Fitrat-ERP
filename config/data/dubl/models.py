from django.db import models

from ..command.models import TimeStampModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

class Dubl(TimeStampModel):
    lid : Lid = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True,related_name='dubl_lid')
    student : Student = models.ForeignKey(Student, on_delete=models.CASCADE,null=True,blank=True,related_name='dubl_student')
    is_okay = models.BooleanField(default=False)
    on_merge = models.BooleanField(default=False)
    message = models.TextField(null=True,blank=True)

    def __str__(self):
        return f"Dubled {self.student.phone_number if self.student else self.lid.phone_number}"