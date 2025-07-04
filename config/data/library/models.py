from django.db import models

from ..command.models import BaseModel
from ..upload.models import File
# Create your models here.


class Category(BaseModel):
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name


class Library(BaseModel):
    category : "Category" = models.ForeignKey("library.Category", on_delete=models.SET_NULL, null=True,blank=True)
    name = models.TextField()
    choice = models.CharField(choices=[
        ("withAudio", "With Audio"),
        ("noAudio", "No Audio"),
    ],max_length=100,null=True,blank=True)

    book : "File" = models.ForeignKey("upload.File", on_delete=models.SET_NULL, null=True,blank=True, related_name="books_files")

    file : "File" = models.ManyToManyField("upload.File",related_name="libraries_files")
    def __str__(self):
        return self.name

