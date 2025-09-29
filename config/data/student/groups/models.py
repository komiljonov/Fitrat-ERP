from datetime import timedelta
from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import now

from data.command.models import BaseModel

if TYPE_CHECKING:
    from data.student.course.models import Course
    from data.student.student.models import Student
    from data.lid.new_lid.models import Lid
    from data.student.subject.models import Level
    from data.student.studentgroup.models import StudentGroup
    from data.student.attendance.models import Attendance
    from data.employee.models import Employee
    from data.student.subject.models import Theme


class Room(BaseModel):
    room_number = models.CharField(
        max_length=100,
    )
    room_filling = models.FloatField(default=10, null=True, blank=True)

    room_type = models.CharField(
        choices=[
            ("LESSON_ROOM", "Dars xonasi"),
            ("COWORKING_ZONE", "Coworking zone"),
        ],
        default="LESSON_ROOM",
    )

    def __str__(self):
        return self.room_number


class Day(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    display_name = models.CharField(max_length=255)

    index = models.IntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return f"Day({self.name} index={self.index})"


def one_year_from_now():
    return timezone.now() + timedelta(days=365)


class Group(BaseModel):
    name = models.CharField(max_length=100)

    course: "Course" = models.ForeignKey(
        "course.Course",
        on_delete=models.CASCADE,
        related_name="groups_course",
    )

    level: "Level | None" = models.ForeignKey(
        "subject.Level",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="groups_level",
    )

    teacher: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teachers_groups",
    )

    secondary_teacher: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="secondary_teacher",
    )

    status = models.CharField(
        choices=[
            ("ACTIVE", "Active"),
            ("PENDING", "Pending"),
            ("INACTIVE", "Inactive"),
        ],
        default="ACTIVE",
        max_length=100,
    )

    room_number: "Room" = models.ForeignKey("groups.Room", on_delete=models.CASCADE)

    price_type = models.CharField(
        choices=[
            ("DAILY", "Daily payment"),
            ("MONTHLY", "Monthly payment"),
        ],
        default="DAILY",
        max_length=100,
    )

    price = models.FloatField(default=0, null=True, blank=True)

    scheduled_day_type: "models.ManyToManyField[Day]" = models.ManyToManyField(
        "groups.Day"
    )  # Correct Many-to-ManyField definition

    is_secondary = models.BooleanField(
        default=False, help_text="Is there secondary group?"
    )

    started_at = models.TimeField(default=now)
    ended_at = models.TimeField(default=now)

    start_date = models.DateTimeField(default=timezone.now)

    finish_date = models.DateTimeField(default=one_year_from_now)

    comment = models.TextField(null=True, blank=True)

    students: "models.QuerySet[StudentGroup]"
    attendances: "models.QuerySet[Attendance]"
    lessons: "models.QuerySet[GroupLesson]"

    def __str__(self):
        return f"{self.name} - {self.price_type}"


class GroupLesson(BaseModel):
    """Guruhni aynan biron kun uchun o'tilgan darslari haqida ma'lumot"""

    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="lessons",
    )

    date = models.DateField()

    theme: "Theme | None" = models.ForeignKey(
        "subject.Theme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
    )

    is_repeat = models.BooleanField(
        default=False,
        help_text="Bu kundagi dars takrorlashmidi yoki yo'q.",
    )

    class Meta(BaseModel.Meta):

        constraints = [
            *BaseModel.Meta.constraints,
            # Keep one lesson per day per group
            models.UniqueConstraint(
                fields=["group", "date"],
                name="unique_group_date",
            ),
            # Theme must be unique within a group when NOT a repeat.
            # Allows duplicates when is_repeat=True and also ignores NULL themes.
            models.UniqueConstraint(
                fields=["group", "theme"],
                name="unique_theme_per_group_when_not_repeat",
                condition=Q(is_repeat=False, theme__isnull=False),
            ),
        ]


class GroupSaleStudent(BaseModel):
    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.CASCADE,
        related_name="sale_student_group",
    )
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sale_student_student",
    )
    lid: "Lid" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sale_student_lid",
    )
    amount = models.FloatField(default=0, null=True, blank=True)

    comment = models.TextField(null=True, blank=True)


class SecondaryGroup(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    group: "Group" = models.ForeignKey("groups.Group", on_delete=models.CASCADE)

    teacher: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    scheduled_day_type: "Day" = models.ManyToManyField(
        "groups.Day",
        related_name="secondary_scheduled_day_type",
    )

    status = models.CharField(
        choices=[
            ("ACTIVE", "Active"),
            ("PENDING", "Pending"),
            ("INACTIVE", "Inactive"),
        ],
        default="ACTIVE",
        max_length=100,
    )

    started_at = models.TimeField(default=now)  # Use timezone-aware default
    ended_at = models.TimeField(default=now)

    start_date = models.DateTimeField(default=timezone.now)
    finish_date = models.DateTimeField(default=timezone.now)

    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
