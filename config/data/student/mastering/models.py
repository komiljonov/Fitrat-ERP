from django.db import models

from data.exam_results.models import LevelExam
from data.exam_results.models import MockExam
from data.student.quiz.models import Quiz
from data.student.student.models import Student
from data.student.subject.models import Theme
from data.account.models import CustomUser
from data.command.models import BaseModel
from data.lid.new_lid.models import Lid


# Create your models here.
class Mastering(BaseModel):
    theme: "Theme" = models.ForeignKey(
        Theme,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastering_theme",
    )

    lid: "Lid" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    test: "Quiz" = models.ForeignKey(
        "quiz.Quiz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    choice = models.CharField(
        choices=[
            ("Homework", "Homework"),
            ("Test", "Test"),
            ("Speaking", "Speaking"),
            ("Unit_Test", "Unit_Test"),
            ("Mock", "Mock"),
            ("MidCourse", "Mi1dCourse"),
            ("Level", "Level"),
        ],
        default="Homework",
        null=True,
        blank=True,
    )

    mock: "MockExam | None" = models.ForeignKey(
        "exam_results.MockExam",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastering_mock",
    )

    updater = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastering_updater",
    )

    ball = models.FloatField(default=0)
    level_exam: "LevelExam" = models.ForeignKey(
        "exam_results.LevelExam",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mastering_level_exam",
    )

    # def __str__(self):
    #     return self.lid.first_name if self.lid else self.student.first_name

    class Meta:
        ordering = ("created_at",)


class MasteringTeachers(BaseModel):
    teacher: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teacher_mastering",
    )
    reason = models.TextField(blank=True, null=True)
    bonus = models.BooleanField(default=False)
    ball = models.FloatField(max_length=255, default=0)

    def __str__(self):
        return f"{self.teacher.first_name} {self.ball}"
