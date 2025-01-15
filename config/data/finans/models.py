from django.contrib.auth import get_user_model
from django.db import models

from ..command.models import TimeStampModel

User = get_user_model()

class Finans(TimeStampModel):
    Action_choise = (
        ('INCOME', 'INCOME'),
        ('EXPENSE', 'EXPENSE'),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

