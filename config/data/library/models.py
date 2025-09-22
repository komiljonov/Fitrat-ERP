from django.db import models

from data.command.models import BaseModel
from data.upload.models import File

# Create your models here.


class LibraryCategory(BaseModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Library(BaseModel):
    category: "LibraryCategory" = models.ForeignKey(
        "library.LibraryCategory", on_delete=models.SET_NULL, null=True, blank=True
    )
    name = models.TextField()
    choice = models.CharField(
        choices=[
            ("withAudio", "With Audio"),
            ("noAudio", "No Audio"),
        ],
        max_length=100,
        null=True,
        blank=True,
    )

    description = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    author = models.CharField(max_length=256, null=True, blank=True)

    cover = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_images",
    )

    book: "File" = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="books_files",
    )

    file: "File" = models.ManyToManyField("upload.File", related_name="libraries_files")

    def __str__(self):
        return self.name
