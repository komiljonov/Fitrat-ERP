import hashlib

from django.db import models
from django.utils import timezone

from ...account.models import CustomUser
from ...command.models import TimeStampModel
from ...department.filial.models import Filial
from ...department.marketing_channel.models import MarketingChannel
from ...upload.models import File


class Student(TimeStampModel):
    photo = models.ForeignKey('upload.File', on_delete=models.SET_NULL,null=True,blank=True,related_name='students_photo')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(max_length=100)
    date_of_birth = models.DateField(default=timezone.now())

    password = models.CharField(max_length=100,null=True,blank=True,default=hashlib.sha256("1".encode()).hexdigest())

    language_choice = (("ENG", "ENG"),
                       ("RU", "RU"),
                       ("UZB", "UZB"))

    education_lang = models.CharField(choices=language_choice, default="UZB", max_length=100)
    student_type = models.CharField(max_length=100, default="student")
    edu_class = models.CharField(choices=[
        ("SCHOOL", "School"),
        ("UNIVERSITY", "University"),
        ("NONE", "None"),
    ], default="NONE",
        max_length=100,
        help_text="Education level at school if student studies at school")
    edu_level = models.CharField(null=True, blank=True, max_length=100)
    subject = models.ForeignKey("subject.Subject", on_delete=models.SET_NULL, null=True, blank=True,
                                help_text="Subject that student won at competition")
    ball = models.IntegerField(default=0, null=True, blank=True, help_text="Earned ball at competition")

    filial: "Filial" = models.ForeignKey("filial.Filial", on_delete=models.CASCADE, null=True, blank=True,
                                         help_text="Filial for this student")
    marketing_channel: "MarketingChannel" = models.ForeignKey("marketing_channel.MarketingChannel",
                                                              on_delete=models.CASCADE, null=True, blank=True,
                                                              help_text="Marketing channel for this student")

    student_stage_type = models.CharField(
        choices=(
            ('NEW_STUDENT', 'NEW_STUDENT'),
            ('ACTIVE_STUDENT', 'ACTIVE_STUDENT'),
        ),
        default="NEW_STUDENT",
        max_length=100,
        help_text="Student stage type",
    )

    new_student_stages = models.CharField(
        choices=[
            ('BIRINCHI_DARS', 'BIRNCHI_DARS'),
            ("GURUH_O'ZGARTIRGAN", "GURUH_O'ZGARTIRGAN"),
            ("QARIZDOR", "QARIZDOR"),
        ],
        default="BIRNCHI_DARS",
        null=True,
        blank=True,
        max_length=100,
        help_text="Student stage type",
    )
    balance = models.FloatField(default=0)

    balance_status = models.CharField(
        choices=[
            ('ACTIVE', 'ACTIVE'),
            ('INACTIVE', 'INACTIVE'),
        ],
        default='INACTIVE',
        max_length=100,
        help_text="Balance status",
    )

    service_manager: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, null=True,
                                                blank=True, help_text="service_manager for this student",
                                                related_name="student_service_manager")

    sales_manager: "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, null=True, )
    is_archived = models.BooleanField(default=False, help_text="Is this student archived or not")
    is_frozen = models.BooleanField(default=False, help_text="Is this student frozen or not")

    file : "File" = models.ManyToManyField('upload.File', blank=True,
                related_name="student_files", help_text="File for this student")

    call_operator: 'CustomUser' = models.ForeignKey('account.CustomUser', on_delete=models.SET_NULL,
                                                    null=True, blank=True, help_text="Call operator",
                                                    related_name="student_call_operator")
    def __str__(self):
        return f"{self.first_name} {self.subject} {self.ball} in {self.student_stage_type} stage"
