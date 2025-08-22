from django.db import models

from data.account.models import CustomUser
from data.student.student.models import Student
from ..command.models import BaseModel
from ..student.course.models import Course
from ..student.groups.models import Group
from ..student.subject.models import Subject


class QuizResult(BaseModel):
    quiz = models.ForeignKey(
        "quiz.Quiz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_results",
    )
    student: "Student" = models.ForeignKey(
        "student.Student", on_delete=models.SET_NULL, null=True, blank=True
    )
    questions = models.ManyToManyField("quiz.Question", related_name="quiz_results")
    match_pair = models.ManyToManyField("quiz.MatchPairs", related_name="quiz_results")
    true_false = models.ManyToManyField("quiz.True_False", related_name="quiz_results")
    vocabulary = models.ManyToManyField("quiz.Vocabulary", related_name="quiz_results")
    objective = models.ManyToManyField(
        "quiz.ObjectiveTest", related_name="quiz_results"
    )
    cloze_test = models.ManyToManyField("quiz.Cloze_Test", related_name="quiz_results")
    image_objective = models.ManyToManyField(
        "quiz.ImageObjectiveTest", related_name="quiz_results"
    )
    Listening = models.ManyToManyField("quiz.Listening", related_name="quiz_results")
    point = models.IntegerField(default=0)

    json_body = models.JSONField(default=list)


class UnitTest(BaseModel):
    theme_after = models.ForeignKey(
        "subject.Theme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unit_test_theme_after",
    )
    themes = models.ManyToManyField("subject.Theme", related_name="unit_test_themes")
    quiz = models.ForeignKey(
        "quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True
    )
    group: "Group | None" = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        related_name="unit_test_group",
    )


class UnitTestResult(BaseModel):
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    unit = models.ForeignKey(
        "exam_results.UnitTest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    point = models.IntegerField(default=0)


class MockExam(BaseModel):
    options: "Subject" = models.ForeignKey(
        "subject.Subject",
        on_delete=models.SET_NULL,
        related_name="mock_exam_options",
        null=True,
        blank=True,
    )
    course: "Course" = models.ForeignKey(
        "course.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mock_exam_courses",
    )
    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mock_exam_groups",
    )
    start_date = models.DateField(null=False, blank=False)
    start_time = models.TimeField(null=False, blank=False)

    end_date = models.DateField(null=False, blank=False)
    end_time = models.TimeField(null=False, blank=False)

    # def __str__(self):
    #     return self.group.name


class MockExamResult(BaseModel):
    mock: "MockExam" = models.ForeignKey(
        "exam_results.MockExam",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mock_exam_results",
    )
    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mock_exam_student",
    )
    reading = models.IntegerField(default=0)
    listening = models.IntegerField(default=0)
    writing = models.IntegerField(default=0)
    speaking = models.IntegerField(default=0)

    updater: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mock_exam_updater",
    )

    overall_score = models.IntegerField(default=0)

    # def __str__(self):
    #     return f"{self.student.first_name}  {self.overall_score}"


class LevelExam(BaseModel):
    name = models.CharField(max_length=120, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    choice = models.CharField(
        choices=[
            ("MidCourse", "MidCourse"),
            ("Level", "Level"),
        ],
        max_length=20,
        null=False,
        blank=False,
    )
    course: "Course" = models.ForeignKey(
        "course.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="level_courses_mock",
    )
    group: "Group" = models.ForeignKey(
        "groups.Group",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="level_course_groups_mock",
    )
    subject: "Subject" = models.ForeignKey(
        "subject.Subject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="level_subject_mock",
    )

    def __str__(self):
        return self.name

# class LevelExamResult(BaseModel):
#     level: "LevelExam" = models.ForeignKey(
#         "exam_results.LevelExam", on_delete=models.SET_NULL,null=True,blank=True,related_name="level_exam_results"
#     )
#     student: "Student" = models.ForeignKey(
#         "student.Student", on_delete=models.SET_NULL,null=True,blank=True,related_name="level_exam_student"
#     )
#     ball = models.IntegerField(default=0)
#
#     def __str__(self):
#         return self.level.name
