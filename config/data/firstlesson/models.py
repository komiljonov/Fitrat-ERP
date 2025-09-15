from typing import TYPE_CHECKING
from django.db import models
from django.contrib import admin


from data.command.models import BaseModel

if TYPE_CHECKING:
    from data.student.groups.models import Group
    from data.lid.new_lid.models import Lid
    from data.employee.models import Employee

# Create your models here.


class FirstLesson(BaseModel):

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="first_lessons",
    )

    date = models.DateTimeField()

    status = models.CharField(
        max_length=255,
        choices=[
            ("PENDING", "Kutilmoqda"),
            ("DIDNTCOME", "Darsga kelmadi."),
            ("CAME", "CAME"),
        ],
        default="PENDING",
    )

    comment = models.TextField(null=True, blank=True)

    creator: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_archived = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Sinov darsi"

        verbose_name_plural = "Sinov darslari"

    class Admin(admin.ModelAdmin):

        list_display = ["lead", "group", "date", "status", "comment", "creator"]

        search_fields = [
            "lead__first_name",
            "lead__last_name",
            "lead__middle_name",
            "lead__phone_number",
        ]

        list_filter = ["status", "group"]

        date_hierarchy = "date"
