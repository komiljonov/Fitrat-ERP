from django.db import models

from data.command.models import BaseModel
from data.student.subject.models import Theme
from ...upload.models import File

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

    class Meta:
        verbose_name = "Homework"
        verbose_name_plural = "Homeworks"

    def __str__(self):
        return self.title

