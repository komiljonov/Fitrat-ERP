from django.db import models

from data.account.models import CustomUser
from ...command.models import TimeStampModel

class Employee_attendance(TimeStampModel):
    user : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name="employee_attendance")
    action = models.CharField(choices=[
        ("In_office","In_office"),
        ("Gone","Gone"),
        ("Apsent","Apsent"),
    ],max_length=120, null=True, blank=True)

    type = models.CharField(choices=[
        ("On_time","On_time"),
        ("Late","Late"),
    ], max_length=120, null=True, blank=True)

    is_there = models.DateTimeField(auto_now_add=True)
    is_gone = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name}  {self.action} {self.is_there if self.is_there  else self.is_gone if self.is_gone else "Kelmagan"}"



