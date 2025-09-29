from datetime import timedelta

from django.db import models
from django.utils import timezone

from data.command.models import BaseModel


class MarketingChannel(BaseModel):
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name


# class Group_Type(BaseModel):
#     price_type = models.CharField(
#         choices=[
#             ("DAILY", "Daily payment"),
#             ("MONTHLY", "Monthly payment"),
#         ],
#         default="DAILY",
#         max_length=100,
#     )

#     comment = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return self.price_type


class ConfirmationCode(models.Model):
    phone = models.CharField(max_length=20, unique=True)
    code = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created_at > timezone.now() - timedelta(minutes=1)
