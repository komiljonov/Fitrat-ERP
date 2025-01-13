from typing import Any
from uuid import uuid4
from django.db import models
from django.utils import timezone
from django.contrib import admin





class TimeStampModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # Custom manager for soft delete
    class SoftDeleteManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(deleted_at__isnull=True)

    objects = SoftDeleteManager()
    all_objects = (
        models.Manager()
    )  # Manager to access all objects, including deleted ones

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using=using, keep_parents=keep_parents)

    def restore(self):
        self.deleted_at = None
        self.save()


class OrderedTimestampModel(TimeStampModel):
    order = models.IntegerField(default=0)

    class Meta:
        abstract = True

        ordering = ["order"]