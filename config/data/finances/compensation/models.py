from django.db import models

# Create your models here.

from data.command.models import TimeStampModel


class Compensation(TimeStampModel):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

class Bonus(TimeStampModel):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)




