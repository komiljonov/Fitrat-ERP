from django.db import models

from ..account.models import CustomUser

class Teacher(CustomUser):
    balance = models.FloatField(default=0)

    def __str__(self):
        return self.full_name

