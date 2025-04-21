from django.db import models
from django.utils import timezone

from data.account.models import CustomUser
from ...command.models import BaseModel

class Employee_attendance(BaseModel):
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

    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name}   {self.action}   {self.type}"


