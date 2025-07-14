from django.db import models

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data.account.models import CustomUser
    from data.command.models import BaseModel


class Filial(models.Model):
    name = models.CharField(max_length=100)

    latitude = models.FloatField(default=0.0)
    longitude = models.FloatField(default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name


class UserFilial(BaseModel):
    filial : "Filial" = models.ForeignKey("filial.Filial", on_delete=models.SET_NULL, null=True, blank=True,related_name="userfilial_filial")
    user : "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.SET_NULL, null=True, blank=True,related_name="userfilial_user")

    is_archived = models.BooleanField(default=False)
