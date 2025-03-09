from typing import TYPE_CHECKING

from django.db import models

from data.command.models import TimeStampModel

if TYPE_CHECKING:
    from ...account.models import CustomUser

class Compensation(TimeStampModel):
    name = models.CharField(max_length=256)
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name}  {self.amount}"


class Bonus(TimeStampModel):
    name = models.CharField(max_length=256)
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def __str__(self):
        return f"{self.name}  {self.amount}"


class Page(TimeStampModel):
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE)
    name = models.CharField(max_length=256)
    is_editable = models.BooleanField(default=False)
    is_readable = models.BooleanField(default=False)

    is_parent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name, self.is_editable, self.is_readable, self.is_parent}"

class Asos(TimeStampModel):
    asos1 = models.DecimalField(decimal_places=2, max_digits=10,verbose_name="1 chi asos buyicha beriladigan ball")
    asos2 = models.DecimalField(decimal_places=2, max_digits=10,verbose_name="2 chi asos buyicha beriladigan ball")
    asos3 = models.DecimalField(decimal_places=2, max_digits=10,verbose_name="3 chi asos buyicha beriladigan ball")
    asos4 = models.DecimalField(decimal_places=2, max_digits=10,verbose_name="4 chi asos buyicha beriladigan ball")
    asos5 = models.DecimalField(decimal_places=2, max_digits=10,verbose_name="5 chi asos buyicha beriladigan ball")


