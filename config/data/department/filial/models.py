from django.db import models
from ...command.models import TimeStampModel
class Filial(TimeStampModel):
    name = models.CharField(max_length=100)
    price = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name