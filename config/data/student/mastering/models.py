from django.db import models

from ..student.models import Student
from ...command.models import TimeStampModel
from ..quiz.models import Quiz


# Create your models here.
class Mastering(TimeStampModel):

    student : "Student" = models.ForeignKey('student.Student', on_delete=models.CASCADE)
    test : "Quiz" = models.ForeignKey('quiz.Quiz', on_delete=models.CASCADE)

    ball = models.FloatField(default=0)

