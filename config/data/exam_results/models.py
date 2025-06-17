from django.db import models

from ..command.models import BaseModel
from ..student.quiz.models import Quiz,Exam,Question,MatchPairs,True_False,Vocabulary,ObjectiveTest,ImageObjectiveTest,Listening,Cloze_Test
from ..student.student.models import Student
from ..student.subject.models import Theme

class QuizResult(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,related_name="quiz_result")
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True)
    questions : "Question" = models.ManyToManyField("quiz.Question", related_name="quiz_result")
    match_pair : "MatchPairs" = models.ManyToManyField("quiz.MatchPairs", related_name="quiz_result_match_pair")
    true_false : "True_False" = models.ManyToManyField("quiz.True_False", related_name="quiz_result_true_false")
    vocabulary : "Vocabulary" = models.ManyToManyField("quiz.Vocabulary", related_name="quiz_result_vocabulary")
    objective : "ObjectiveTest" = models.ManyToManyField("quiz.ObjectiveTest", related_name="quiz_result_objective_test")
    cloze_test : "Cloze_Test" = models.ManyToManyField("quiz.Cloze_Test", related_name="quiz_result_cloze_test")
    image_objective : "ImageObjectiveTest" = models.ManyToManyField("quiz.ImageObjectiveTest", related_name="quiz_result_image_objective_test")
    Listening : "Listening" = models.ManyToManyField("quiz.Listening", related_name="quiz_result_listening")

    point = models.IntegerField(default=0)


class UnitTest(BaseModel):
    theme_after : "Theme" = models.ForeignKey("subject.Theme", on_delete=models.SET_NULL, null=True, blank=True,related_name="unit_test__theme")
    themes : "Theme" = models.ManyToManyField("subject.Theme", related_name="unit_test_theme")
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True)


class UnitTestResult(BaseModel):
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True)
    unit : "UnitTest" = models.ForeignKey("unit.UnitTest", on_delete=models.SET_NULL, null=True, blank=True)
    point = models.IntegerField(default=0)

