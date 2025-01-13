from django.contrib.auth import get_user_model
from django.db import models

from ..command.models import TimeStampModel
from ..lid.new_lid.models import Lid
from ..student.student.models import Student

User = get_user_model()

class Finans(TimeStampModel):
    Action_choise = (
        ('INCOME', 'INCOME'),
        ('EXPENSE', 'EXPENSE'),
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)

