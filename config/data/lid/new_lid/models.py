
from django.db import models
from django.utils import timezone

from ...command.models import TimeStampModel
from ...department.filial.models import Filial
from ...department.marketing_channel.models import MarketingChannel
from ...stages.models import NewLidStages, NewOredersStages
from ...account.models import CustomUser
from ...student.lesson.models import Lesson


class Lid(TimeStampModel):

    sender_id = models.CharField(max_length=120,null=True,blank=True)
    message_text = models.CharField(max_length=120,null=True,blank=True)

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=100,unique=True)
    date_of_birth = models.DateField(default=timezone.now())

    language_choise = (("ENG","ENG"),
                       ("RU","RU"),
                       ("UZB","UZB"))

    education_lang = models.CharField(choices=language_choise,default="UZB",max_length=100)
    student_type = models.CharField(max_length=100, default="student")
    edu_class = models.CharField(max_length=100, help_text="Education level at school if student studies at school")
    subject = models.CharField(max_length=100,null=True, help_text="Subject that student won at competition")
    ball = models.IntegerField(default=0, null=True, blank=True, help_text="Earned ball at competition")

    filial : Filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True, help_text="Filial for this student")
    marketing_channel : MarketingChannel = models.ForeignKey(MarketingChannel, on_delete=models.CASCADE,null=True, blank=True, help_text="Marketing channel for this student")

    lid_stage_type = models.CharField(
        choices=(
        ("NEW_LID","NEW_LID"),
        ("ORDERED_LID","ORDERED_LID"),
        ),
        max_length=100,default="NEW_LID"
    )
    lid_stages : "NewLidStages" = models.ForeignKey("stages.NewLidStages", on_delete=models.CASCADE,null=True, blank=True, help_text="NewStudentStages for this student")
    ordered_stages : "NewOredersStages" = models.ForeignKey("stages.NewOredersStages", on_delete=models.CASCADE,null=True, blank=True, help_text="NewStudentStages for this student")

    first_lesson : "Lesson" = models.ForeignKey("lesson.Lesson", on_delete=models.CASCADE,
                                                related_name="students_first_lesson",
                                                null=True, blank=True,
                                                help_text="Lesson for this lesson")

    is_archived = models.BooleanField(default=False,help_text="Is this student archived or not")

    is_dubl = models.BooleanField(default=False,help_text="Is this student duble or not")

    call_operator : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, null=True, blank=True,help_text="CallOperator for this lid", related_name="call_operator")

    is_student = models.BooleanField(default=False,help_text="Is this student or not")

    moderator : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.CASCADE, null=True, blank=True,)

    lid_stages : models.QuerySet['NewLidStages']
    ordered_stages : models.QuerySet['NewOredersStages']


    def __str__(self):
        return f"{self.first_name} {self.subject} {self.ball} in {self.lid_stages} stage"

