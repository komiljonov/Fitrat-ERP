from django.db import models

from data.account.models import CustomUser
from data.command.models import BaseModel
from data.student.subject.models import Theme
from ...upload.models import File
from ..student.models import Student

class Homework(BaseModel):
    theme : "Theme" = models.ForeignKey("subject.Theme", on_delete=models.CASCADE,
                              related_name="themes_homework")
    title = models.TextField()
    body = models.TextField()
    video : "File" = models.ManyToManyField("upload.File",blank=True,
                                            related_name="homeworks_video")
    documents : "File" = models.ManyToManyField("upload.File",blank=True,
                                                related_name="homework_documents")
    photo : "File" = models.ManyToManyField("upload.File",blank=True,
                                            related_name="homework_photo")
    choice = models.CharField(choices=[
        ("Online", "Online"),
        ("Offline", "Offline"),
    ],max_length=20,null=True,blank=True)

    class Meta:
        verbose_name = "Homework"
        verbose_name_plural = "Homeworks"

    def __str__(self):
        return self.title



class Homework_history(BaseModel):
    homework : "Homework" = models.ForeignKey("homeworks.Homework",
            on_delete=models.CASCADE,related_name="homeworks_history")
    student : "Student" = models.ForeignKey("student.Student",
            on_delete=models.CASCADE,related_name="student_homeworks_history")
    status = models.CharField(choices=[
        ("Passed", "Passed"),
        ("Failed", "Failed"),
        ("Retake", "Retake")
    ], max_length=20,null=True,blank=True)
    is_active = models.BooleanField(default=False)
    mark = models.IntegerField(default=0)
    updater : "CustomUser" = models.ForeignKey("account.CustomUser",on_delete=models.SET_NULL,
                                        null=True,blank=True,related_name="homeworks_updater")
    description = models.TextField(null=True,blank=True)

    class Meta:
        verbose_name = "Homeworks History"
        verbose_name_plural = "Histories"
        ordering = ['created_at']