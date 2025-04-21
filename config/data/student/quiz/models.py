from django.db import models

from data.command.models import BaseModel
from data.student.student.models import Student
from data.student.subject.models import Subject


class Quiz(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    theme : "Subject" = models.ForeignKey('subject.Theme', on_delete=models.SET_NULL,
                              null=True,blank=True, related_name='quiz_theme')

    def __str__(self):
        return self.title

class Answer(BaseModel):
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text

class QuizGaps(BaseModel):
    name = models.CharField(max_length=255, null=True,blank=True)


class Question(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL,null=True,blank=True)
    text : "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL,
                                          null=True,blank=True, related_name="questions_gaps")
    answers : "Answer" = models.ManyToManyField("quiz.Answer", related_name="questions_answers")

    def __str__(self):
        return self.text.name


class Vocabulary(BaseModel):
    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='vocabularies_quiz')
    photo = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_photo')
    voice = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='vocabulary_voice')
    in_english = models.CharField(max_length=255, null=True,blank=True)
    in_uzbek = models.CharField(max_length=255, null=True,blank=True)
    def __str__(self):
        return f"{self.quiz.name}    {self.in_english}    {self.in_uzbek}"


class Gaps(BaseModel):
    name = models.CharField(max_length=255, null=True,blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name

class Fill_gaps(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='fill_gaps_quiz')
    question : "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,related_name='fill_gaps_question')
    gaps : "Gaps" = models.ManyToManyField("quiz.Gaps")

    def __str__(self):
        return f"{self.quiz.title}    {self.question.name}"


class Listening(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='listening_quiz')
    voice = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='listening_voice')
    question : "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,related_name='listening_question')
    answers : "Answer" = models.ManyToManyField(Answer)
    def __str__(self):
        return f"{self.quiz.title}    {self.question.name}"



class Pairs(BaseModel):
    pair = models.CharField(max_length=255)
    choice = models.CharField(choices=[
        ("Left", "Left"),
        ("Right", "Right")
    ])
    def __str__(self):
        return self.pair


class MatchPairs(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='match_pairs_quiz')
    pairs : "Pairs" = models.ManyToManyField("quiz.Pairs",related_name='match_pairs_pair')
    def __str__(self):
        return f"{self.quiz.title} "


class Exam(BaseModel):
    quiz : "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True,blank=True,related_name='exam_quiz')
    type = models.CharField(choices=[
        ("Online", "Online"),
        ("Offline", "Offline"),
    ],max_length=255, null=True,blank=True)
    students = models.ManyToManyField(Student)
    subject : "Subject" = models.ForeignKey("subject.Subject", on_delete=models.SET_NULL, null=True, blank=True,related_name='exam_subject')
    students_xml = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_students_xml')
    exam_materials = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_materials')
    results = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True, related_name='exam_results')

    end_date = models.DateTimeField(null=True,blank=True)

    def __str__(self):
        return f"{self.quiz.title}    {self.type}"