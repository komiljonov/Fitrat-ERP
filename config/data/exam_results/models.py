from django.db import models

from ..command.models import BaseModel
from ..student.quiz.models import Quiz,Exam,Question,MatchPairs,True_False,Vocabulary,ObjectiveTest,ImageObjectiveTest,Listening,Cloze_Test
from ..student.student.models import Student
from ..student.subject.models import Theme
class QuizResult(BaseModel):
    quiz = models.ForeignKey(
        "quiz.Quiz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quiz_results"
    )
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    questions = models.ManyToManyField(
        "quiz.Question",
        related_name="quiz_results"
    )
    match_pair = models.ManyToManyField(
        "quiz.MatchPairs",
        related_name="quiz_results"
    )
    true_false = models.ManyToManyField(
        "quiz.True_False",
        related_name="quiz_results"
    )
    vocabulary = models.ManyToManyField(
        "quiz.Vocabulary",
        related_name="quiz_results"
    )
    objective = models.ManyToManyField(
        "quiz.ObjectiveTest",
        related_name="quiz_results"
    )
    cloze_test = models.ManyToManyField(
        "quiz.Cloze_Test",
        related_name="quiz_results"
    )
    image_objective = models.ManyToManyField(
        "quiz.ImageObjectiveTest",
        related_name="quiz_results"
    )
    Listening = models.ManyToManyField(
        "quiz.Listening",
        related_name="quiz_results"
    )
    point = models.IntegerField(default=0)


class UnitTest(BaseModel):
    theme_after = models.ForeignKey(
        "subject.Theme",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="unit_test_theme_after"
    )
    themes = models.ManyToManyField(
        "subject.Theme",
        related_name="unit_test_themes"
    )
    quiz = models.ForeignKey(
        "quiz.Quiz",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class UnitTestResult(BaseModel):
    student = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    unit = models.ForeignKey(
        "exam_results.UnitTest",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    point = models.IntegerField(default=0)