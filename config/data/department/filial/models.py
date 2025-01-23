from django.db import models


class Filial(models.Model):
    name = models.CharField(max_length=100)

    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name

