from django.contrib.auth import get_user_model
from django.db import models

from ..command.models import TimeStampModel
from django.apps import apps

from ..lid.new_lid.models import Lid
from ..student.student.models import Student

User = get_user_model()

class Comment(TimeStampModel):

    creator : User = models.ForeignKey(User, on_delete=models.CASCADE)
    lid : Lid = models.ForeignKey(Lid, on_delete=models.CASCADE, null=True,blank=True)
    student : Student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True,blank=True)
    comment : str = models.TextField()

    def __str__(self):
        return self.comment