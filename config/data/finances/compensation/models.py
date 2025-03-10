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
    name = models.CharField(max_length=256)


    def __str__(self):
        return f"{self.name} "

class Point(TimeStampModel):
    name = models.CharField(max_length=256)
    asos : "Asos" = models.ForeignKey('compensation.Asos', on_delete=models.CASCADE)
    max_ball = models.DecimalField(decimal_places=2, max_digits=10)


class Monitoring(TimeStampModel):
    user : "CustomUser" = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE,related_name='user_monitoring')
    point : "Point" = models.ForeignKey('compensation.Point', on_delete=models.CASCADE,related_name='point_monitoring')
    ball = models.DecimalField(decimal_places=2, max_digits=10, help_text="This ball can not be higher than asos's max_ball !!!")

    def __str__(self):
        return f"{self.user.full_name}  {self.point.name}  {self.ball} / {self.point.max_ball}"

