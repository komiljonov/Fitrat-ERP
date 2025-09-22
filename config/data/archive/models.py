from typing import TYPE_CHECKING
from django.db import models

from data.command.models import BaseModel


if TYPE_CHECKING:
    from data.comments.views import Comment
    from data.employee.models import Employee
    from data.lid.new_lid.models import Lid
    from data.student.student.models import Student

# Create your models here.


class Archive(BaseModel):

    creator: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archives",
    )

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive",
    )

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archives",
    )

    obj_status = models.CharField(
        max_length=255,
        choices=[
            ("NEW_STUDENT", "Yangi o'quvchi"),
            ("ACTIVE_STUDENT", "Aktiv o'quvchi"),
            ("NEW_LEAD", "Yangi Lead"),
            ("ORDER", "Buyurtma"),
            ("FIRST_LESSON", "Sinov darsi"),
        ],
    )

    reason = models.TextField()
    comment: "Comment | None" = models.ForeignKey(
        "comments.Comment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive",
    )

    unarchived_at = models.DateTimeField(null=True, blank=True)

    unarchived_by = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unarchives",
    )
