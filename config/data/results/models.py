from django.db import models

from data.account.models import CustomUser
from data.command.models import TimeStampModel
from data.student.student.models import Student
from data.upload.models import File
# Create your models here.

class Results(TimeStampModel):
    results = models.CharField(choices=[
        ("University" , "entering to the university" ),
        ("Certificate", "Geting certificate")
    ],
    default="University",
    max_length=100,
    )
    teacher : "CustomUser" = models.ForeignKey("account.CustomUser",
                                               on_delete=models.CASCADE,related_name="teacher_results")
    student : "Student" = models.ForeignKey("student.Student", on_delete=models.CASCADE,related_name="student_results")


    university_type = models.CharField(choices=[
        ("Official", "Official"),
        ("Unofficial", "Unofficial"),
        ("Foreign_university", "Foreign_university"),
    ],
    default="Official",
    max_length=100,null=True,blank=True)
    university_name = models.CharField(max_length=120,null=True,blank=True)
    university_entering_type = models.CharField(choices=[
        ("Grant", "Grant"),
        ("Kontrakt", "Kontrakt"),
        ("Super_Kontrakt", "Super_Kontrakt"),
    ],
    default="Kontrakt",
    max_length=100,null=True,blank=True)
    university_entering_ball = models.FloatField(null=True,blank=True)


    certificate_type = models.CharField(choices=[
        ("IELTS", "IELTS"),
        ("CEFR", "CEFR"),
        ("SAT","SAT"),
        ("OTHER","OTHER"),
    ],
    default="IELTS",
    max_length=100,null=True,blank=True
    )
    band_score = models.FloatField(null=True,blank=True)
    reading_score = models.FloatField(null=True,blank=True)
    lessoning_score = models.FloatField(null=True,blank=True)
    speaking_score = models.FloatField(null=True,blank=True)
    writing_score = models.FloatField(null=True,blank=True)

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

    def __str__(self):
        return self.certificate_type