from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.utils import timezone

if TYPE_CHECKING:
    from data.account.models import CustomUser

from data.department.filial.models import Filial


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    filial: "Filial" = models.ForeignKey('filial.Filial', on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']


class UserFilial(BaseModel):
    filial: "Filial" = models.ForeignKey("filial.Filial", on_delete=models.SET_NULL, null=True, blank=True,
                                         related_name="userfilial_filial")
    user: "CustomUser" = models.ForeignKey("account.CustomUser", on_delete=models.SET_NULL, null=True, blank=True,
                                           related_name="userfilial_user")

    is_archived = models.BooleanField(default=False)
