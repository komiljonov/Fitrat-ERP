from typing import TYPE_CHECKING

from django.db import models

from data.account.models import CustomUser

if TYPE_CHECKING:
    from data.student.subject.models import Theme
from ..groups.models import Group
from ..subject.models import Subject
from ...command.models import TimeStampModel
from ...lid.new_lid.models import Lid
from ...student.student.models import Student


class Lesson(TimeStampModel):
    name = models.CharField(max_length=100)
    subject: 'Subject' = models.ForeignKey(
        'subject.Subject', on_delete=models.SET_NULL, null=True, blank=True
    )
    group: "Group" = models.ForeignKey(
        "groups.Group", on_delete=models.CASCADE, related_name="lessons"
    )

    theme: 'Theme' = models.ForeignKey('subject.Theme', on_delete=models.SET_NULL, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)
    type = models.CharField(
        choices=[
            ("Lesson", "Lesson"),
            ("Repeat", "Repeat"),
        ],
        default="Lesson",
        max_length=100,
    )

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
        return f"Lesson {self.name}      {self.group}      Room {self.group.room_number}"


class FirstLLesson(TimeStampModel):
    lid: 'Lid' = models.ForeignKey(
        'new_lid.Lid', on_delete=models.SET_NULL, null=True, blank=True
    )

    group: 'Group' = models.ForeignKey(
        'groups.Group', on_delete=models.SET_NULL, null=True, blank=True
    )

    date = models.DateField(null=True, blank=True)
    time = models.TimeField(null=True, blank=True)

    comment = models.TextField(null=True, blank=True)

    creator: 'CustomUser' = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.lid.first_name}      {self.group.name}     {self.date}     {self.time}"


class ExtraLessonGroup(TimeStampModel):
    group: "Group" = models.ForeignKey(
        'groups.Group', on_delete=models.SET_NULL, null=True, blank=True, related_name="groups_extra_lesson"
    )
    room : "Room" = models.ForeignKey(
        'groups.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name="extra_group_lessons_room"
    )
    date = models.DateField(null=True, blank=True)
    started_at = models.TimeField(null=True, blank=True)
    ended_at = models.TimeField(null=True, blank=True)
    creator: 'CustomUser' = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True,
        related_name="groups_extra_lesson_creator"
    )
    comment = models.TextField(null=True, blank=True)
    is_payable = models.BooleanField(default=False)
    is_attendance = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.group.name}      {self.date}      {self.started_at}      {self.is_payable}      {self.is_attendance}"


from ..groups.models import Room


class ExtraLesson(TimeStampModel):
    student: "Student" = models.ForeignKey(
        'student.Student', on_delete=models.SET_NULL, null=True, blank=True, related_name="students_extra_lesson"
    )
    teacher: "CustomUser" = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True, related_name="teachers_extra_lesson"
    )
    date = models.DateField(null=True, blank=True)
    started_at = models.TimeField(null=True, blank=True)
    ended_at = models.TimeField(null=True, blank=True)
    room: "Room" = models.ForeignKey(
        'groups.Room', on_delete=models.SET_NULL, null=True, blank=True, related_name="rooms_extra_lesson"
    )
    comment = models.TextField(null=True, blank=True)
    creator: 'CustomUser' = models.ForeignKey(
        'account.CustomUser', on_delete=models.SET_NULL, null=True, blank=True
    )
    is_payable = models.BooleanField(default=False)
    is_attendance = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student.phone}      {self.date}      {self.started_at}      {self.is_payable}      {self.is_attendance}"
