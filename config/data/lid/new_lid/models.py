from django.db import models
from django.utils import timezone

from data.student.student.models import Student
from ...account.models import CustomUser
from ...command.models import BaseModel
from ...department.filial.models import Filial
from ...department.marketing_channel.models import MarketingChannel
from ...upload.models import File


class Lid(BaseModel):
    sender_id = models.CharField(max_length=120, null=True, blank=True)
    message_text = models.CharField(max_length=120, null=True, blank=True)

    photo: "File" = models.ForeignKey('upload.File',
                                      on_delete=models.SET_NULL,
                                      null=True, blank=True,
                                      related_name='lids_photo')

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(default=timezone.now())
    extra_number = models.CharField(max_length=100, null=True, blank=True)
    language_choise = (("ENG", "ENG"),
                       ("RU", "RU"),
                       ("UZB", "UZB"))

    education_lang = models.CharField(choices=language_choise, default="UZB", max_length=100)
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

    filial: Filial = models.ForeignKey(Filial, on_delete=models.SET_NULL,
                                       null=True, blank=True,
                                       help_text="Filial for this student")

    marketing_channel: "MarketingChannel" = models.ForeignKey("marketing_channel.MarketingChannel",
                                                            on_delete=models.SET_NULL,
                                                            null=True, blank=True,
                                                            help_text="Marketing channel for this student")

    lid_stage_type = models.CharField(
        choices=(
            ("NEW_LID", "NEW_LID"),
            ("ORDERED_LID", "ORDERED_LID"),
        ),
        max_length=100, default="NEW_LID"
    )
    lid_stages = models.CharField(choices=[
        ("YANGI_LEAD", "YANGI_LEAD"),
        ("KUTULMOQDA", "KUTULMOQDA"),
    ],
        max_length=100,
        help_text="LID's YANGI_LEAD stage type",
        null=True, blank=True
    )
    is_expired = models.BooleanField(default=False)
    ordered_stages = models.CharField(
        choices=[
            ("KUTULMOQDA", "KUTULMOQDA"),
            ("BIRINCHI_DARS_BELGILANGAN", "BIRINCHI_DARS_BELGILANGAN"),
            ("YANGI_BUYURTMA", "YANGI_BUYURTMA"),
        ],
        max_length=100,
        help_text="LID's YANGI_LEAD stage type",
        null=True, blank=True
    )
    is_archived = models.BooleanField(default=False, help_text="Is this student archived or not")

    is_dubl = models.BooleanField(default=False, help_text="Is this student duble or not")

    is_frozen = models.BooleanField(default=False, help_text="Is this student frozen or not")

    call_operator: "CustomUser" = models.ForeignKey("account.CustomUser",
                                                    on_delete=models.SET_NULL,
                                                    null=True, blank=True,
                                                    help_text="CallOperator for this lid",
                                                    related_name="call_operator")

    is_student = models.BooleanField(default=False, help_text="Is this student or not")

    service_manager: "CustomUser" = models.ForeignKey("account.CustomUser",
                                                      on_delete=models.SET_NULL,
                                                      null=True, blank=True,
                                                      related_name='service_manager')


    sales_manager: "CustomUser" = models.ForeignKey('account.CustomUser',
        on_delete=models.CASCADE, null=True,blank=True, related_name="sales_manager")

    file: "File" = models.ManyToManyField("upload.File",
                                          related_name="lid_file", blank=True)

    ordered_date = models.DateTimeField(null=True, blank=True)

    student : "Student" = models.ForeignKey("student.Student", on_delete=models.SET_NULL,
                                            null=True,blank=True,)

    balance = models.FloatField(default=0)

    def __str__(self):
        return f"{self.first_name} {self.subject} {self.ball} in {self.lid_stages} stage"
