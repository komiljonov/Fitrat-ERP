from django.db import models

from ...finances.compensation.models import Compensation,Bonus
from ...lid.new_lid.models import Lid
from ..student.models import Student
from ...command.models import TimeStampModel
from ..quiz.models import Quiz
from ..groups.models import Group
from ...account.models import CustomUser

# Create your models here.
class Mastering(TimeStampModel):

    lid : "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.SET_NULL , null=True,blank=True)
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL , null=True,blank=True)
    test : "Quiz" = models.ForeignKey('quiz.Quiz', on_delete=models.SET_NULL , null=True,blank=True)
    # group : "Group" = models.ForeignKey('group.Group', on_delete=models.SET_NULL , null=True,blank=True)


    ball = models.FloatField(default=0)

    def __str__(self):
        return  self.lid.first_name if self.lid else self.student.first_name + " " + self.ball

class MasteringTeachers(TimeStampModel):
    teacher : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL ,
                                               null=True,blank=True,
                                               related_name='teacher_mastering')
    compensation : "Compensation" = models.ForeignKey('compensation.Compensation',
                                                      on_delete=models.SET_NULL ,
                                                      null=True,blank=True,
                                                      related_name='compensation_mastering')
    bonus : "Bonus" = models.ForeignKey('compensation.Bonus', on_delete=models.SET_NULL ,null=True,blank=True,related_name='bonus_mastering')
    ball = models.FloatField(max_length=255, default=0)
    def __str__(self):
        return f"{self.teacher.first_name} {self.ball}"
