from django.db import models

from ...command.models import BaseModel

class MarketingChannel(BaseModel):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return self.name


class Group_Type(BaseModel):
    price_type = models.CharField(choices=[
        ('DAILY', 'Daily payment'),
        ('MONTHLY', 'Monthly payment'),
    ],
        default='DAILY',
        max_length=100)
    def __str__(self):
        return self.price_type