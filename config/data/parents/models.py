from django.db import models

from data.account.models import CustomUser
from ..command.models import BaseModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


# Create your models here.


class Relatives(BaseModel):
    name = models.CharField(null=True, blank=True, max_length=100)
    phone = models.CharField(null=True, blank=True, max_length=100)
    who = models.CharField(null=True, blank=True, max_length=100)

    lid: "Lid" = models.ForeignKey(
        "new_lid.Lid", on_delete=models.SET_NULL, null=True, blank=True
    )
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="relatives_student",
    )

    user: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_parent",
    )


def __str__(self):
    return f"{self.who}"
