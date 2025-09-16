from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q

from data.command.models import BaseModel

from data.student.attendance.choices import AttendanceStatusChoices

if TYPE_CHECKING:
    from data.student.subject.models import Theme
    from data.lid.new_lid.models import Lid
    from data.student.student.models import Student
    from data.student.groups.models import Group, SecondaryGroup
    from data.firstlesson.models import FirstLesson


class Attendance(BaseModel):

    date = models.DateField()

    theme: "models.ManyToManyField[Theme]" = models.ManyToManyField(
        "subject.Theme",
        blank=True,
        related_name="attendance_theme",
    )

    group: "Group | None" = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendances",
    )

    repeated = models.BooleanField(default=False)

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendances",
    )

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="attendances",
    )

    first_lesson: "FirstLesson | None" = models.ForeignKey(
        "firstlesson.FirstLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )

    status = models.CharField(
        max_length=20,
        choices=AttendanceStatusChoices.CHOICES,
        default=AttendanceStatusChoices.UNREASONED,
        help_text="Attendance reason (Sababli/Sababsiz)",
    )

    comment: str = models.TextField(blank=True, null=True, help_text="Comment")

    amount = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Attendance counted amount ...",
    )

    attended_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f" {self.group} is marked as {self.status}"

    class Meta:
        constraints = [
            # Exactly one of student or lid must be set (XOR)
            models.CheckConstraint(
                name="attendance_xor_student_or_lead",
                check=(
                    (Q(student__isnull=True) & Q(lead__isnull=False))
                    | (Q(student__isnull=False) & Q(lead__isnull=True))
                ),
            ),
            # Unique per (date, group, student) when student is set
            models.UniqueConstraint(
                fields=["date", "group", "student"],
                name="attendance_unique_date_group_student",
                condition=Q(student__isnull=False),
            ),
            # Unique per (date, group, lead) when lead is set
            models.UniqueConstraint(
                fields=["date", "group", "lead"],
                name="attendance_unique_date_group_lead",
                condition=Q(lead__isnull=False),
            ),
        ]


class SecondaryAttendance(BaseModel):
    theme: "Theme | None" = models.ForeignKey(
        "subject.Theme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_group_attendance",
    )
    group: "SecondaryGroup | None" = models.ForeignKey(
        "groups.SecondaryGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendances",
    )
    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_attendances",
    )

    status = models.CharField(
        max_length=20,
        choices=AttendanceStatusChoices.CHOICES,
        default=AttendanceStatusChoices.UNREASONED,
        help_text="Attendance holati (Sababli/Sababsiz)",
    )

    comment: str = models.TextField(blank=True, null=True)

    def __str__(self):
        return f" {self.group} is marked as {self.reason}"
