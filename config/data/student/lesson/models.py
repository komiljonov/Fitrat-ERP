from django.db import models
from ...command.models import TimeStampModel
from ..groups.models import Group


class Lesson(TimeStampModel):
    name = models.CharField(max_length=100,)
    subject = models.CharField(max_length=100)

    group : "Group" = models.ForeignKey("groups.Group", on_delete=models.CASCADE,
                                      related_name="group")
    comment = models.TextField()

    lesson_status = models.CharField(
        choices=[
            ("ACTIVE", "Active"),
            ("FINISHED", "Finished"),
        ],
        default="ACTIVE",
        max_length=20,
    )
    lessons_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Lesson {self.name} | {self.group}"

