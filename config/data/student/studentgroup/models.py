from typing import TYPE_CHECKING
from django.db import models
from django.db.models import Q

from data.command.models import BaseModel

if TYPE_CHECKING:
    from data.student.student.models import Student
    from data.lid.new_lid.models import Lid
    from data.student.groups.models import Group, SecondaryGroup


class StudentGroup(BaseModel):

    group: "Group | None" = models.ForeignKey(
        "groups.Group",
        on_delete=models.PROTECT,
        related_name="student_groups",
    )

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students_group",
    )

    lid: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lid_groups",
    )

    is_archived = models.BooleanField(default=False)

    HOMEWORK_ONLINE = "Online"
    HOMEWORK_OFFLINE = "Offline"

    homework_type = models.CharField(
        choices=[(HOMEWORK_ONLINE, "Online"), (HOMEWORK_OFFLINE, "Offline")],
        default=HOMEWORK_OFFLINE,
        null=True,
        blank=True,
        max_length=20,
    )

    class Meta:
        verbose_name = "Student Group"
        verbose_name_plural = "Student Groups"

        constraints = [
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
        ]

    def __str__(self):
        return self.group.name if self.group else ""


class SecondaryStudentGroup(BaseModel):
    group: "SecondaryGroup | None" = models.ForeignKey(
        "groups.SecondaryGroup",
        on_delete=models.PROTECT,
    )
    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        related_name="students_secondary_group",
        null=True,
        blank=True,
    )
    lid: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        related_name="lids_secondary_group",
        null=True,
        blank=True,
    )

    is_archive = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Secondary Add group"
        verbose_name_plural = "Secondary Add group"

        constraints = [
            # No duplicate active student in the same group
            models.UniqueConstraint(
                fields=["group", "student"],
                name="uniq_active_student_in_secondary_group",
                condition=Q(student__isnull=False, is_archive=False),
                # deferrable=models.Deferrable.DEFERRED,  # optional but nice for bulk ops
            ),
            # No duplicate active lid in the same group
            models.UniqueConstraint(
                fields=["group", "lid"],
                name="uniq_active_lid_in_secondary_group",
                condition=Q(lid__isnull=False, is_archive=False),
                # deferrable=models.Deferrable.DEFERRED,
            ),
        ]
