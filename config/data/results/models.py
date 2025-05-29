from django.db import models

from data.account.models import CustomUser
from data.command.models import BaseModel
from data.student.student.models import Student
from data.upload.models import File
# Create your models here.

class Results(BaseModel):

    who = models.CharField(choices=[
        ("Mine","Mine"),
        ("Student","Student"),
    ],max_length=20, null=True, blank=True)

    results = models.CharField(choices=[
        ("University" , "entering to the university"),
        ("Certificate", "Geting certificate"),
        ("Olimpiada", "Olimpiada natijalari")
    ],
    max_length=100,null=True,
    blank=True,
    )

    teacher : "CustomUser" = models.ForeignKey("account.CustomUser",
                            on_delete=models.CASCADE,related_name="teacher_results")
    student : "Student" = models.ForeignKey("student.Student",
                            on_delete=models.CASCADE,related_name="student_results")


    national = models.ForeignKey("subject.Subject",on_delete=models.SET_NULL,
                                 null=True,blank=True, related_name="national_results",
                                 help_text="National sertificate subject")

    university_type = models.CharField(choices=[
        ("Official", "Official"),
        ("Unofficial", "Unofficial"),
        ("Foreign_university", "Foreign_university"),
    ],
    max_length=100,null=True,blank=True)
    university_name = models.CharField(max_length=120,null=True,blank=True)
    university_entering_type = models.CharField(choices=[
        ("Grant", "Grant"),
        ("Kontrakt", "Kontrakt")
    ],
    max_length=100,null=True,blank=True)
    university_entering_ball = models.FloatField(null=True,blank=True)

    degree = models.CharField(choices=[
        ("1","1"),
        ("2","2"),
        ("3","3"),
    ],
    max_length=100,null=True,blank=True)
    level = models.CharField(choices=[
        ("Region", "Region"),
        ("Regional", "Regional"),
    ], max_length=256, null=True, blank=True)

    # certificate_type = models.CharField(choices=[
    #     ("IELTS", "IELTS"),
    #     ("CEFR", "CEFR"),
    #     ("SAT","SAT"),
    #     ("OTHER","OTHER"),
    # ],
    # max_length=100,null=True,blank=True
    # )
    result_fk_name = models.ForeignKey("compensation.ResultName",on_delete=models.SET_NULL,
                                    null=True,blank=True, related_name="monitoring_result_name")
    band_score = models.CharField(max_length=10,null=True,blank=True)
    reading_score = models.FloatField(null=True,blank=True)
    listening_score = models.FloatField(null=True,blank=True)
    speaking_score = models.FloatField(null=True,blank=True)
    writing_score = models.FloatField(null=True,blank=True)

    result_name = models.CharField(max_length=120,null=True,blank=True)
    result_score = models.FloatField(default=0,null=True,blank=True)
    subject_name = models.CharField(max_length=120,null=True,blank=True)


    upload_file : "File" = models.ManyToManyField("upload.File")
    status = models.CharField(
        choices=[
            ("Accepted", "Accepted"),
            ("Rejected", "Rejected"),
            ("In_progress", "in_progress"),
        ],
        default="In_progress",
        max_length=100,
    )
    updater : "CustomUser" = models.ForeignKey("account.CustomUser",on_delete=models.SET_NULL,related_name="updater_results",null=True,blank=True)

    def __str__(self):
        return f"{self.results} -- {self.student.first_name}"

 