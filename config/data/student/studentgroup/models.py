from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q, CheckConstraint
from django.core.exceptions import ValidationError
from django.utils import timezone


from data.command.models import BaseModel
from data.logs.models import Log

if TYPE_CHECKING:
    from data.student.student.models import Student
    from data.lid.new_lid.models import Lid
    from data.student.groups.models import Group, SecondaryGroup
    from data.firstlesson.models import FirstLesson


class StudentGroup(BaseModel):

    group: "Group | None" = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="students",
    )

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="groups",
    )

    lid: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="groups",
    )

    first_lesson: "FirstLesson | None" = models.ForeignKey(
        "firstlesson.FirstLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups",
    )

    HOMEWORK_ONLINE = "Online"
    HOMEWORK_OFFLINE = "Offline"

    homework_type = models.CharField(
        choices=[(HOMEWORK_ONLINE, "Online"), (HOMEWORK_OFFLINE, "Offline")],
        default=HOMEWORK_OFFLINE,
        null=True,
        blank=True,
        max_length=20,
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Student Group"
        verbose_name_plural = "Student Groups"

        ordering = ["-created_at"]

        constraints = [
            *BaseModel.Meta.constraints,
            # No duplicate active student in the same group
            models.UniqueConstraint(
                fields=["group", "student"],
                name="uniq_active_student_in_group",
                condition=Q(student__isnull=False, is_archived=False),
                # deferrable=models.Deferrable.DEFERRED,  # optional but nice for bulk ops
            ),
            # No duplicate active lid in the same group
            models.UniqueConstraint(
                fields=["group", "lid"],
                name="uniq_active_lid_in_group",
                condition=Q(lid__isnull=False, is_archived=False),
                # deferrable=models.Deferrable.DEFERRED,
            ),
            # Make first_lesson required if lead is presented
            CheckConstraint(
                name="lead_requires_first_lesson_when_active",
                condition=Q(is_archived=True)
                | Q(lid__isnull=True)
                | Q(first_lesson__isnull=False),
            ),
            # Require student or lead or both to be set.
            CheckConstraint(
                name="student_or_lid_required",
                condition=Q(student__isnull=False) | Q(lid__isnull=False),
            ),
        ]

    def __str__(self):
        return self.group.name if self.group else ""

    def clean(self):
        super().clean()
        if not self.is_archived and self.lid_id and not self.first_lesson_id:
            raise ValidationError(
                {
                    "first_lesson": "First lesson is required when a lead (lid) is set for an active record."
                }
            )

    def streak(self):
        """Get streak of UNREASONED DIDNTCOME attendance for this student or lead."""

        from data.student.attendance.models import Attendance

        if self.student:
            return Attendance.streak_for_student(self.group, self.student)

        if self.lid:
            return Attendance.streak_for_lead(self.group, self.lid)

        raise Exception("Student or Lead must be provided.")

    def archive(self, comment: str):

        self.archived_at = timezone.now()
        self.is_archived = True

        self.save()

        Log.object.filter(
            object="STUDENT",
            action="ARCHIVE_STUDENT_GROUP",
            student=self.student,
            student_group=self,
            comment=f"O'quvchi guruhi archivelandi. Comment: {comment}",
        )


class SecondaryStudentGroup(BaseModel):

    group: "SecondaryGroup | None" = models.ForeignKey(
        "groups.SecondaryGroup",
        on_delete=models.PROTECT,
    )

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        related_name="secondary_groups",
        null=True,
        blank=True,
    )

    lid: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        related_name="secondary_groups",
        null=True,
        blank=True,
    )

    class Meta(BaseModel.Meta):
        verbose_name = "Secondary Add group"
        verbose_name_plural = "Secondary Add group"

        constraints = [
            *BaseModel.Meta.constraints,
            # No duplicate active student in the same group
            models.UniqueConstraint(
                fields=["group", "student"],
                name="uniq_active_student_in_secondary_group",
                condition=Q(student__isnull=False, is_archived=False),
                # deferrable=models.Deferrable.DEFERRED,  # optional but nice for bulk ops
            ),
            # No duplicate active lid in the same group
            models.UniqueConstraint(
                fields=["group", "lid"],
                name="uniq_active_lid_in_secondary_group",
                condition=Q(lid__isnull=False, is_archived=False),
                # deferrable=models.Deferrable.DEFERRED,
            ),
        ]
