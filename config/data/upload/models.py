from django.db import models
from django.http import HttpRequest

from ..command.models import BaseModel


class File(BaseModel):
    choice = models.CharField(choices=[
        ("file", "File"),
        ("link", "Link"),
    ],default="file",max_length=120, null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    file = models.FileField(upload_to="files/", null=True, blank=True)


class Contract(BaseModel):
    file = models.FileField(upload_to="files/", null=True, blank=True)
