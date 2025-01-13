from django.db import models

from ..account.models import CustomUser

class Moderator(CustomUser):

    balance = models.DecimalField(max_digits=10, decimal_places=2)


