from django.db import models

from data.command.models import BaseModel
from data.student.student.models import Student


class Store(BaseModel):
    photo = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True,blank=True, related_name="store_photo")
    video = models.ForeignKey("upload.File",on_delete=models.CASCADE,related_name="uploaded_store")
    seen = models.BooleanField(default=False)


class Strike(BaseModel):
    student : "Student" = models.ForeignKey("student.Student",on_delete=models.CASCADE,related_name="student_strike")

    def __str__(self):
        return self.student.phone

class VersionUpdate(BaseModel):
    app_name = models.CharField(choices=[
        ("Teacher", "Teacher"),
        ("Student", "Student"),
        ("ASSISTANT", "ASSISTANT"),
    ],null=True,blank=False,max_length=100)
    version = models.CharField(max_length=10,unique=True)
    should_update = models.BooleanField(default=False)
    forced_update = models.BooleanField(default=False)
    def __str__(self):
        return self.version
