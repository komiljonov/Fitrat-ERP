from django.db import models

from ..command.models import BaseModel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..lid.new_lid.models import Lid
    from ..student.student.models import Student
    from ..account.models import CustomUser
    from ..upload.models import File


class Comment(BaseModel):

    creator: "CustomUser" = models.ForeignKey(
        "account.CustomUser", on_delete=models.CASCADE
    )
    file: "File" = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="comments_photo",
    )
    lid: "Lid" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    comment: str = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.comment

    class Meta(BaseModel.Meta):
        ordering = []


class StuffComments(BaseModel):
    comment: str = models.TextField(null=True, blank=True)
    file: "File" = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stuff_comments_photo",
    )
    creator: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        related_name="comments_stuff",
    )
    stuff: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="comments_stuff_user",
    )
