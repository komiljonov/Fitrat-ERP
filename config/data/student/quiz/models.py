from datetime import datetime, timedelta

from django.db import models

from data.command.models import BaseModel
from data.student.homeworks.models import Homework
from data.student.student.models import Student
from data.student.subject.models import Subject
from data.student.subject.models import Theme
from data.upload.models import File
from data.student.groups.models import Group



def after_4_days():
    return datetime.today() + timedelta(days=4)

class Quiz(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    theme: "Theme" = models.ForeignKey('subject.Theme', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='quiz_theme')

    subject: "Subject" = models.ForeignKey('subject.Subject', on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='quiz_subject')

    homework: "Homework" = models.ForeignKey('homeworks.Homework', on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name="quiz_homework", )
    type = models.CharField(choices=[
        ("Online", "Online"),
        ("Offline", "Offline"),
    ], default="Offline", max_length=255, null=True, blank=True)

    count = models.IntegerField(default=20)
    time = models.IntegerField(default=60)

    def __str__(self):
        return self.title


class Answer(BaseModel):
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizGaps(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)


class Question(BaseModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.SET_NULL, null=True, blank=True)
    text: "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL,
                                         null=True, blank=True, related_name="questions_gaps")
    answers: "Answer" = models.ManyToManyField("quiz.Answer", related_name="questions_answers")

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_file")

    # def __str__(self):
    #     return self.text.name


class Vocabulary(BaseModel):
    quiz = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name='vocabularies_quiz')
    photo = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='vocabulary_photo')
    voice = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='vocabulary_voice')
    in_english = models.CharField(max_length=255, null=True, blank=True)
    in_uzbek = models.CharField(max_length=255, null=True, blank=True)

    comment = models.TextField(blank=True, null=True)
    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_vocab_file")


class Gaps(BaseModel):
    name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return self.name


class Fill_gaps(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='fill_gaps_quiz')
    question: "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='fill_gaps_question')
    gaps: "Gaps" = models.ManyToManyField("quiz.Gaps")

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_fill_file")

    # def __str__(self):
    #     return f"{self.quiz.title}    {self.question.name}"


class Listening(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='listening_quiz')
    voice = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='listening_voice')
    question: "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='listening_question')
    type = models.CharField(choices=[
        ("MultipleChoice", "MultipleChoice"),
        ("TFG", "True False Not Given"),
        ("YNG", "Yes No Not Given"),
        ("Fill_gaps", "Fill Gaps"),

    ])
    answers: "Answer" = models.ManyToManyField(Answer)

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_lesson_file")


class Pairs(BaseModel):
    pair = models.CharField(max_length=255)
    choice = models.CharField(choices=[
        ("Left", "Left"),
        ("Right", "Right")
    ])
    key = models.CharField(max_length=255)

    def __str__(self):
        return self.pair


class MatchPairs(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='match_pairs_quiz')
    pairs: "Pairs" = models.ManyToManyField("quiz.Pairs", related_name='match_pairs_pair')

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_match_file")

    # def __str__(self):
    #     return f"{self.quiz.title} "


class ObjectiveTest(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='objectivetest_quiz')
    question: "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='objectivetest_question')
    answers: "Answer" = models.ManyToManyField(Answer)

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_objective_file")

    # def __str__(self):
    #     return f"{self.quiz.title}    {self.question.name}"


class Cloze_Test(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='clozetest_quiz')
    questions: "QuizGaps" = models.ManyToManyField("quiz.QuizGaps", related_name='cloze_questions')
    sentence: "Answer" = models.ForeignKey("quiz.Answer", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='cloze_answer')

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_cloze_file")


class ImageObjectiveTest(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='image_cloze_quiz')
    image: "File" = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='image_cloze_quiz')
    answer: "Answer" = models.ForeignKey("quiz.Answer", on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name='image_cloze_answer')

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_image_file")

    # def __str__(self):
    #     return f"{self.quiz.title}  {self.answer.text}"


class True_False(BaseModel):
    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='True_False_test_quiz')
    question: "QuizGaps" = models.ForeignKey("quiz.QuizGaps", on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='True_False_test_question')
    answer = models.CharField(choices=[
        ("True", "True"),
        ("False", "False"),
        ("Not Given", "Not Given"),
    ], max_length=15, null=True, blank=True)

    comment = models.TextField(blank=True, null=True)

    file = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                             related_name="question_boolen_file")

    # def __str__(self):
    #     return f"{self.quiz.title}  {self.answer}"


class ExamSubject(BaseModel):
    subject: "Subject" = models.ForeignKey("subject.Subject", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='exam_subject_quiz')

    options = models.CharField(default=1, max_length=2, null=True, blank=True)

    lang_foreign = models.BooleanField(default=False)
    lang_national = models.BooleanField(default=False)

    order = models.IntegerField(null=True, blank=True)

    has_certificate = models.BooleanField(default=False)
    certificate: "File" = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='certificate_of_student')
    certificate_expire_date = models.DateField(null=True, blank=True)


class Exam(BaseModel):
    name = models.CharField(default="Test imtihoni", null=False, blank=False)

    quiz: "Quiz" = models.ForeignKey("quiz.Quiz", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='exam_quiz')

    choice = models.CharField(choices=[
        ("Weekly", "Weekly"),
        ("Monthly", "Monthly"),
        ("Unit", "Unit"),
        ("Mid_of_course", "Mid_of_course"),
        ("Level", "Level"),
        ("Mock", "Mock"),
        ("Homework", "Homework"),
    ], max_length=255, null=True, blank=True)

    type = models.CharField(choices=[
        ("Online", "Online"),
        ("Offline", "Offline"),
    ], default="Offline", max_length=255, null=True, blank=True)

    is_mandatory = models.BooleanField(default=False)

    # students = models.ManyToManyField(Student)
    students_xml = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='exam_students_xml')

    results = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                                related_name='exam_results')

    materials = models.ManyToManyField('upload.File', related_name='quiz_materials')

    lang_foreign = models.BooleanField(default=False)
    lang_national = models.BooleanField(default=False)

    is_language = models.BooleanField(default=False)

    date = models.DateField(default=after_4_days)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)

    homework: "Homework" = models.ForeignKey('homeworks.Homework', on_delete=models.SET_NULL, null=True, blank=True,
                                             related_name='homeworks_quiz')
    options = models.ManyToManyField("quiz.ExamSubject", related_name='exam_subject_options')


class ExamRegistration(BaseModel):
    student: "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='registrated_student')
    exam: "Exam" = models.ForeignKey("quiz.Exam", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='registration_exam')
    status = models.CharField(choices=[
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Waiting", "Waiting"),
    ], max_length=255, null=True, blank=True)

    variation = models.CharField(choices=[
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    ], max_length=2, null=True, blank=True)

    is_participating = models.BooleanField(default=True)
    mark = models.CharField(max_length=255, null=True, blank=True)
    student_comment = models.TextField(null=True, blank=True)
    group: "Group" = models.ForeignKey("groups.Group", on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='registration_group')
    option: "ExamSubject" = models.ManyToManyField("quiz.ExamSubject", related_name='registration_option_subjects')

    # def __str__(self):
    #     return f"{self.student.first_name}  {self.exam.choice}  {self.mark}  {self.created_at}"


class ExamCertificate(BaseModel):
    student: "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='registrated_student_certificate')
    exam: "Exam" = models.ForeignKey("quiz.Exam", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name='registration_exam_certificate')
    certificate: "File" = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True, blank=True,
                                            related_name='registered_certificate_of_student')

    subject: "Subject" = models.ForeignKey("subject.Subject", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name='certificate_of_student_subject')

    expire_date = models.DateField(null=True, blank=True)

    status = models.CharField(choices=[
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Pending", "Pending"),
    ], max_length=255, null=True, blank=True)

    # def __str__(self):
    #     return f"{self.student.first_name}  {self.status}"
