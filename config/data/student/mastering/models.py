from django.db import models

from ..quiz.models import Quiz
from ..student.models import Student
from ..subject.models import Theme
from ...account.models import CustomUser
from ...command.models import BaseModel
from ...lid.new_lid.models import Lid


# Create your models here.
class Mastering(BaseModel):

    theme : "Theme" = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True,blank=True,
                                        related_name='mastering_theme')
    lid : "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.SET_NULL , null=True,blank=True)
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL , null=True,blank=True)
    test : "Quiz" = models.ForeignKey('quiz.Quiz', on_delete=models.SET_NULL , null=True,blank=True)
    ball = models.FloatField(default=0)

    def __str__(self):
        return self.lid.first_name if self.lid else self.student.first_name

    class Meta:
        ordering = ('created_at',)

class MasteringTeachers(BaseModel):
    teacher : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL ,
                                               null=True,blank=True,
                                               related_name='teacher_mastering')
    reason = models.TextField(blank=True,null=True)
    ball = models.FloatField(max_length=255, default=0)
    def __str__(self):
        return f"{self.teacher.first_name} {self.ball}"


