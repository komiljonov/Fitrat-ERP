from django.contrib.auth import get_user_model
from django.db import models
from rest_framework import request
from typing import TYPE_CHECKING
from ..command.models import TimeStampModel

if TYPE_CHECKING:
    from ..lid.new_lid.models import Lid
    from ..student.student.models import Student
    from ..account.models import CustomUser

class Task(TimeStampModel):
    creator : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name='task_performer')

    lid: "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.CASCADE, null=True, blank=True)
    student: "Student" = models.ForeignKey("student.Student", on_delete=models.CASCADE, null=True, blank=True)

    task = models.TextField()

    performer = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, null=True, blank=True)

    comment = models.TextField(blank=True)

    date_of_expired = models.DateTimeField()

    status = models.CharField(
        choices=[
            ("COMPLATED","COMPLATED"),
            ("EXPIRED",'EXPIRED'),
            ("ONGOING",'ONGOING'),
            ("SOON",'SOON'),
            ("CANCELLED","CANCELLED")
                 ],
        default="SOON",
        max_length=50
    )


    def __str__(self):
        return self.task + " " + str(self.creator) + " " + str(self.status)

