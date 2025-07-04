from django.db import models

# Create your models here.
from ..upload.models import File
from ..command.models import BaseModel

class Event(BaseModel):
    file : "File" = models.ManyToManyField("upload.File",related_name="events_file")
    photo : "File" = models.ForeignKey("upload.File",on_delete=models.SET_NULL,null=True,blank=True,related_name="events_photo")

    link_preview = models.URLField(null=True,blank=True)
    link = models.URLField(null=True,blank=True)
    comment = models.TextField(null=True,blank=True)
    end_date = models.DateField(null=True,blank=True)
    status = models.CharField(choices=[
        ("Expired", "Expired"),
        ("Soon", "Soon"),
    ],default="Soon",max_length=20,null=True,blank=True)

    def __str__(self):
        return self.status
