from typing import TYPE_CHECKING
from django.db import models
from django.contrib import admin


from data.command.models import BaseModel
from data.student.course.models import Course
from data.student.subject.models import Level

if TYPE_CHECKING:
    from data.student.groups.models import Group
    from data.lid.new_lid.models import Lid
    from data.employee.models import Employee
    from data.student.subject.models import Subject

# Create your models here.


class FirstLesson(BaseModel):

    lead: "Lid" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.CASCADE,
        related_name="frist_lessons",
    )

    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="first_lessons",
    )

    teacher: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="first_lessons",
    )

    subject: "Subject" = models.ForeignKey(
        "subject.Subject",
        on_delete=models.CASCADE,
        related_name="first_lessons",
    )

    level: "Level | None" = models.ForeignKey(
        "subject.Level",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="first_lessons",
    )

    course: "Course" = models.ForeignKey(
        "course.Course",
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

    def _sync_from_group(self):
        if self.group_id:
            # these names assume Group has these FKs/fields
            self.teacher = self.group.teacher
            self.subject = self.group.course.subject
            self.level = self.group.level
            self.course = self.group.course
            self.filial = self.lead.filial

    def save(self, *args, **kwargs):
        # always sync before saving (covers creates & updates)
        self._sync_from_group()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Sinov darsi"

        verbose_name_plural = "Sinov darslari"

        constraints = [
            models.UniqueConstraint(
                fields=["lead", "group", "date"], name="unique_lead_group_date"
            )
        ]

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
