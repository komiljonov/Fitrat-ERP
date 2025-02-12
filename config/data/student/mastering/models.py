from django.db import models

from ...lid.new_lid.models import Lid
from ..student.models import Student
from ...command.models import TimeStampModel
from ..quiz.models import Quiz
from ..groups.models import Group


# Create your models here.
class Mastering(TimeStampModel):

    lid : "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.SET_NULL , null=True,blank=True)
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL , null=True,blank=True)
    test : "Quiz" = models.ForeignKey('quiz.Quiz', on_delete=models.SET_NULL , null=True,blank=True)
    group : "Group" = models.ForeignKey('group.Group', on_delete=models.SET_NULL , null=True,blank=True)


    ball = models.FloatField(default=0)

    def __str__(self):
        return  self.lid.first_name if self.lid else self.student.first_name + " " + self.ball