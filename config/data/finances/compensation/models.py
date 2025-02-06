from django.db import models

# Create your models here.

from data.command.models import TimeStampModel


class Compensation(TimeStampModel):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name}  {self.amount}"

class Bonus(TimeStampModel):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    def __str__(self):
        return f"{self.name}  {self.amount}"

class Page(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"