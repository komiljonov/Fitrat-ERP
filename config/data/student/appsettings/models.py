from django.db import models

from data.command.models import BaseModel


class Store(BaseModel):
    video = models.ForeignKey("upload.File",on_delete=models.CASCADE,related_name="uploaded_store")
    seen = models.BooleanField(default=False)




