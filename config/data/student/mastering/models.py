from django.db import models

from ..quiz.models import Quiz
from ..student.models import Student
from ..subject.models import Theme
from ...account.models import CustomUser
from ...command.models import BaseModel
from ...lid.new_lid.models import Lid


# Create your models here.
class Mastering(BaseModel):

    theme : "Theme" = models.ForeignKey(Theme, on_delete=models.SET_NULL, null=True,blank=True,
                                        related_name='mastering_theme')
    lid : "Lid" = models.ForeignKey("new_lid.Lid", on_delete=models.SET_NULL , null=True,blank=True)
    student : "Student" = models.ForeignKey('student.Student', on_delete=models.SET_NULL , null=True,blank=True)
    test : "Quiz" = models.ForeignKey('quiz.Quiz', on_delete=models.SET_NULL , null=True,blank=True)
    ball = models.FloatField(default=0)

    def __str__(self):
        return self.lid.first_name if self.lid else self.student.first_name

    class Meta:
        ordering = ('created_at',)

class MasteringTeachers(BaseModel):
    teacher : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL ,
                                               null=True,blank=True,
                                               related_name='teacher_mastering')
    reason = models.TextField(blank=True,null=True)
    bonus = models.BooleanField(default=False)
    ball = models.FloatField(max_length=255, default=0)
    def __str__(self):
        return f"{self.teacher.first_name} {self.ball}"


# class StudentQuiz(BaseModel):
#     quiz : "Quiz" = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True,blank=True,
#                                       related_name='student_quiz')
#
#     standard_quiz = models.ForeignKey("quiz.Question", on_delete=models.SET_NULL, null=True,blank=True,
#                                       related_name='student_quiz_standard')
#     fill_gap_quiz = models.ForeignKey("quiz.Fill_gaps", on_delete=models.SET_NULL, null=True,blank=True,
#                                       related_name='student_quiz_fill_gaps')
#     vocab_quiz = models.ForeignKey("quiz.Vocabulary", on_delete=models.SET_NULL, null=True,blank=True,
#                                    related_name='student_quiz_vocab')
#     match_quiz = models.ForeignKey("quiz.MatchPairs", on_delete=models.SET_NULL, null=True,blank=True,
#                                    related_name='student_quiz_match_pairs')
#     objective_quiz = models.ForeignKey("quiz.ObjectiveTest", on_delete=models.SET_NULL, null=True,blank=True,
#                                        related_name='student_quiz_objective_test')
#     cloze_quiz = models.ForeignKey("quiz.Cloze_Test", on_delete=models.SET_NULL, null=True,blank=True,
#                                    related_name='student_quiz_cloze')
#     image_quiz = models.ForeignKey("quiz.Image", on_delete=models.SET_NULL, null=True,blank=True,
#                                    related_name='student_quiz_image')
#     true_false_quiz = models.ForeignKey("quiz.TrueFalse", on_delete=models.SET_NULL, null=True,blank=True,
#                                         related_name='student_quiz_true_false')
#
#     time = models.IntegerField(default=0)
#
#     answer = models.ForeignKey("quiz.Answer", on_delete=models.SET_NULL, null=True,blank=True,
#                                related_name='student_quiz_answer')
#
#     is_correct = models.BooleanField(default=False)
#
#     student = models.ForeignKey('student.Student', on_delete=models.SET_NULL, null=True,blank=True,
#                                 related_name='student_quiz_student')
#
#     def __str__(self):
#
#         return f"{self.student.first_name} {self.student.last_name}"