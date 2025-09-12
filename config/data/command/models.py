from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.utils import timezone


if TYPE_CHECKING:
    from data.account.models import CustomUser

from data.command.utils import capture_context_deep
from data.department.filial.models import Filial




class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    filial: "Filial | None" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # New: creation/update call-site snapshots
    create_context = models.JSONField(null=True, blank=True)
    update_context = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        """
        - On create: set create_context once (if absent).
        - On update: refresh update_context to the latest caller site.
        """
        if self._state.adding:  # creating
            if not self.create_context:
                self.create_context = _full_context()
            # Don't pre-fill update_context on create
        else:  # updating
            self.update_context = _full_context()

        super().save(*args, **kwargs)


class UserFilial(BaseModel):
    filial: "Filial" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userfilial_filial",
    )
    user: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="userfilial_user",
    )

    is_archived = models.BooleanField(default=False)
