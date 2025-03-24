from typing import Any
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib import admin

from data.department.filial.models import Filial


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    filial : "Filial" = models.ForeignKey('filial.Filial', on_delete=models.SET_NULL, null=True,blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']
