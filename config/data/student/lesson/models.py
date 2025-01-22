from django.db import models
from ...command.models import TimeStampModel
from ..groups.models import Group
from ..subject.models import Subject

class Lesson(TimeStampModel):
    name = models.CharField(max_length=100)
    subject: 'Subject' = models.ForeignKey(
        'subject.Subject', on_delete=models.SET_NULL, null=True, blank=True
    )
    group: "Group" = models.ForeignKey(
        "groups.Group", on_delete=models.CASCADE, related_name="lessons"
    )

    comment = models.TextField(null=True, blank=True)
    lesson_status = models.CharField(
        choices=[
            ("ACTIVE", "Active"),
            ("FINISHED", "Finished"),
        ],
        default="ACTIVE",
        max_length=20,
    )
    lessons_count = models.IntegerField(default=0)

    start_time = models.TimeField(null=True, blank=True)  # Start time for the lesson
    end_time = models.TimeField(null=True, blank=True)  # End time for the lesson
    day = models.DateField(null=True, blank=True)  # Specific day of the lesson

    def __str__(self):
        return f"Lesson {self.name} | {self.group} | Room {self.group.room_number}"
