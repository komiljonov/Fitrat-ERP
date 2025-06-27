from datetime import datetime
from typing import Optional
from django.db import models
from django.utils import timezone

from data.account.models import CustomUser
from ...command.models import BaseModel


class Employee_attendance(BaseModel):
    employee: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        to_field="second_user",
        on_delete=models.SET_NULL,
        related_name="employee_attendance",
        null=True, blank=True
    )

    attendance: "Stuff_Attendance" = models.ManyToManyField(
        "Stuff_Attendance",
        related_name="employee_full_attendance"
    )
    
    status = models.CharField(
        choices=[
            ("In_office", "In_office"),
            ("Gone", "Gone"),
            ("Absent", "Absent"),
        ], max_length=10, null=True, blank=True
    )
    
    date = models.DateField(default=timezone.now().date())

    amount = models.FloatField(default=0)


class Stuff_Attendance(BaseModel):
    employee: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        to_field="second_user",
        on_delete=models.SET_NULL,
        related_name="employee_part_attendance",
        null=True, blank=True
    )

    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)

    first_check_in = models.DateTimeField(null=True, blank=True)
    first_check_out = models.DateTimeField(null=True, blank=True)

    not_marked = models.BooleanField(default=False)

    date = models.DateField(default=timezone.now().date())

    amount = models.FloatField(default=0)
    actions = models.JSONField(null=True, blank=True)
    action = models.CharField(
        choices=[
            ("In_side", "In_side"),
            ("Outside", "Outside"),
        ], max_length=10, null=True, blank=True
    )
    status = models.CharField(
        choices=[
            ("Late", "Late"),
            ("On_time", "On_time"),
            ("Absent", "Absent"),
        ],max_length=10, null=True, blank=True
    )
    def __str__(self):
        return f"{self.check_in} - {self.check_out} - {self.action}"

    def save(self, *args, **kwargs):
        if self.check_in and not self.first_check_in:
            self.first_check_in = self.check_in

        if self.check_out and not self.first_check_out:
            self.first_check_out = self.check_out

        super().save(*args, **kwargs)

    @property
    def work_time(self) -> Optional["UserTimeLine"]:
        return UserTimeLine.get_todays_wt(self.employee)


    @property
    def work_time_opt(self) -> bool:
        return self.work_time is not None


    @property
    def bonus(self) -> float:
        return self.work_time.bonus if self.work_time else 0.0


class UserTimeLine(BaseModel):
    user: "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, related_name="user_timeline")
    day = models.CharField(choices=[
        ("Monday", "Monday"),
        ("Tuesday", "Tuesday"),
        ("Wednesday", "Wednesday"),
        ("Thursday", "Thursday"),
        ("Friday", "Friday"),
        ("Saturday", "Saturday"),
        ("Sunday", "Sunday"),
    ], max_length=120, null=True, blank=True)

    is_weekend = models.BooleanField(default=False)

    penalty = models.FloatField(default=0)
    bonus = models.FloatField(default=0)

    start_time = models.TimeField(default=timezone.now)
    end_time = models.TimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.full_name}   {self.day}   {self.start_time}   {self.end_time}"

    @staticmethod
    def get_user_wt(employee):
        return UserTimeLine.objects.filter(user=employee).first()
    
    @staticmethod
    def get_todays_wt(employee):
        today_day = datetime.today().strftime("%A")  # 'Monday', 'Tuesday', ...
        return UserTimeLine.objects.filter(user=employee, day=today_day).first()
    