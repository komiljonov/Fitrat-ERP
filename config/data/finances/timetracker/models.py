from django.db import models

from data.account.models import CustomUser
from ...command.models import TimeStampModel

class Employee_attendance(TimeStampModel):
    user : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name="employee_attendance")
    action = models.CharField(choices=[
        ("Is_Present","Is_Present"),
        ("Unreasoned","Unreasoned")
    ],max_length=120, null=True, blank=True)
    is_there = models.DateTimeField(auto_now_add=True)
    is_gone = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name}  {self.action} {self.is_there if self.is_there  else self.is_gone if self.is_gone else "Kelmagan"}"

    def get_total_work_hours(self):
        if self.action == "Is_Present" and self.is_there:
            come = self.is_there
            gone = self.is_gone
            pass


