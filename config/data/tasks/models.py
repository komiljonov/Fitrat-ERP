from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import request

from ..command.models import TimeStampModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

User = get_user_model()

class Task(TimeStampModel):
    creator : User = models.ForeignKey(User, on_delete=models.CASCADE, related_name='task_performer')

    lid: Lid = models.ForeignKey(Lid, on_delete=models.CASCADE, null=True, blank=True)
    student: Student = models.ForeignKey(Student, on_delete=models.CASCADE, null=True, blank=True)

    task = models.TextField()

    comment = models.TextField(blank=True)

    date_of_expired = models.DateTimeField()

    status = models.CharField(
        choices=[
            ("COMPLATED","COMPLATED"),
            ("EXPIRED",'EXPIRED'),
            ("ONGOING",'ONGOING'),
            ("CANCELLED","CANCELLED")
                 ],
        default="WAITING",
        max_length=50
    )


    def __str__(self):
        return self.task + " " + str(self.creator) + " " + str(self.status)

