from django.db import models


class Store(models.Model):
    video = models.ForeignKey("upload.File",on_delete=models.CASCADE,related_name="uploaded_store")
    seen = models.BooleanField(default=False)

    def __str__(self):
        return self.seen



