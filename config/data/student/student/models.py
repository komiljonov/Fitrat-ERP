
from typing import TYPE_CHECKING
from django.db import models
from django.utils import timezone

from ...command.models import TimeStampModel
from ...department.filial.models import Filial
from ...department.marketing_channel.models import MarketingChannel
from ...stages.models import NewStudentStages,StudentStages

from ...account.models import CustomUser

class Student(TimeStampModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100)
    date_of_birth = models.DateField(default=timezone.now())

    language_choice = (("ENG","ENG"),
                       ("RU","RU"),
                       ("UZB","UZB"))

    education_lang = models.CharField(choices=language_choice,default="UZB",max_length=100)
    student_type = models.CharField(max_length=100, default="student")
    edu_class = models.CharField(max_length=100, help_text="Education level at school if student studies at school")
    subject = models.CharField(max_length=100,null=True, help_text="Subject that student won at competition")
    ball = models.IntegerField(default=0, null=True, blank=True, help_text="Earned ball at competition")

    filial : "Filial" = models.ForeignKey("filial.Filial", on_delete=models.CASCADE, null=True, blank=True, help_text="Filial for this student")
    marketing_channel : "MarketingChannel" = models.ForeignKey("marketing_channel.MarketingChannel", on_delete=models.CASCADE,null=True,blank=True, help_text="Marketing channel for this student")

    student_stage_type = models.CharField(
        choices=(
            ('NEW_STUDENT','NEW_STUDENT'),
            ('ACTIVE_STUDENT','ACTIVE_STUDENT'),
        ),
        default="NEW_STUDENT",
        max_length=100,
        help_text="Student stage type",
    )

    new_student_stages : "NewStudentStages" = models.ForeignKey("stages.NewStudentStages", on_delete=models.CASCADE,null=True, blank=True, help_text="NewStudentStages for this student")
    active_student_stages : "StudentStages" = models.ForeignKey('stages.StudentStages', on_delete=models.CASCADE, null=True, blank=True,help_text="StudentStages for this student")

    is_archived = models.BooleanField(default=False, help_text="Is this student archived or not")

    call_operator : 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                                     null=True, blank=True, help_text="Call operator",
                                                     related_name="student_call_operator")

    balance = models.FloatField(default=0)

    moderator : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, null=True,
                                                 blank=True, help_text="Moderator for this student",
                                                 related_name="student_moderator")
    def __str__(self):
        return f"{self.first_name} {self.subject} {self.ball} in {self.new_student_stages} stage"



