from django.db import models

from data.account.models import CustomUser
from data.student.subject.models import Theme
from ...command.models import TimeStampModel
from ..groups.models import Group
from ..subject.models import Subject

from ...lid.new_lid.models import Lid
from ...student.student.models import Student
from ...student.studentgroup.models import StudentGroup


class Lesson(TimeStampModel):
    name = models.CharField(max_length=100)
    subject: 'Subject' = models.ForeignKey(
        'subject.Subject', on_delete=models.SET_NULL, null=True, blank=True
    )
    group: "Group" = models.ForeignKey(
        "groups.Group", on_delete=models.CASCADE, related_name="lessons"
    )

    theme : 'Theme' = models.ForeignKey('subject.Theme', on_delete=models.SET_NULL, null=True, blank=True)
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


class FirstLLesson(TimeStampModel):
    lid : 'Lid' = models.ForeignKey(
        'new_lid.Lid', on_delete=models.SET_NULL, null=True, blank=True
    )

    group: 'Group' = models.ForeignKey(
        'groups.Group', on_delete=models.SET_NULL, null=True, blank=True
    )

    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    creator : 'CustomUser' = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )
