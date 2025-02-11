from django.db import models

from data.command.models import TimeStampModel
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ...account.models import CustomUser

class Compensation(TimeStampModel):
    name = models.CharField(max_length=256)
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    price_type = models.CharField(choices=[
        ('SUM',"Summa"),
        ('PERCENT',"Percent"),
    ],
    default='SUM',
    max_length=10,)

    def __str__(self):
        return f"{self.name}  {self.amount} {self.price_type}"


class Bonus(TimeStampModel):
    name = models.CharField(max_length=256)
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    price_type = models.CharField(choices=[
        ('SUM',"Summa"),
        ('PERCENT',"Percent"),
    ],
    default='SUM',
    max_length=10,)

    def __str__(self):
        return f"{self.name}  {self.amount} {self.price_type}"


class Page(TimeStampModel):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"