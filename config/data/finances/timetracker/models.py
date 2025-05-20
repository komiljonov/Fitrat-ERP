from django.db import models
from django.utils import timezone

from data.account.models import CustomUser
from ...command.models import BaseModel

class Employee_attendance(BaseModel):
    user : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name="employee_attendance")
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    not_marked = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name}   {self.check_in}   {self.check_out}"


class UserTimeLine(BaseModel):
    user : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name="user_timeline")
    day = models.CharField(choices=[
        ("Monday","Monday"),
        ("Tuesday","Tuesday"),
        ("Wednesday","Wednesday"),
        ("Thursday","Thursday"),
        ("Friday","Friday"),
        ("Saturday","Saturday"),
        ("Sunday","Sunday"),
    ],max_length=120, null=True, blank=True)
    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name}   {self.day}   {self.start_time}   {self.end_time}"