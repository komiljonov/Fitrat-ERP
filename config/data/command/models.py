from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.utils import timezone

from django.db.models.fields.files import FieldFile


if TYPE_CHECKING:
    from data.account.models import CustomUser

from data.command.utils import capture_context_deep
from data.department.filial.models import Filial


def _full_context():
    """
    Capture full stack with all locals, no truncation.
    """
    return capture_context_deep(
        stack_max_frames=10**6,  # practically unlimited
        locals_max_items=10**6,
        locals_depth=10**6,
        max_str_len=10**6,
        include_stack_locals=True,
        order="tail",
    )


def _value_for_compare(v):
    # Normalize file fields etc. to a stable comparable value
    if isinstance(v, FieldFile):
        return v.name  # just the path stored in DB
    return v


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

    # ---------- change tracking ----------
    def _capture_initial_state(self):
        """
        Take a snapshot of current concrete field values for later diffing.
        """
        self.__initial_state__ = {
            f.attname: _value_for_compare(getattr(self, f.attname))
            for f in self._meta.concrete_fields  # excludes m2m automatically
        }

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Ensure objects loaded from the DB have their initial state captured.
        """
        instance = super().from_db(db, field_names, values)
        instance._capture_initial_state()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # After constructing (even new objects), capture initial state.
        self._capture_initial_state()

    def changed_fields(self) -> list[str]:
        """
        Return a list of concrete field *names* (model attribute names)
        whose current values differ from the captured initial state.
        Works for both new (unsaved) and existing instances.
        """
        initial = getattr(self, "__initial_state__", {}) or {}
        changed: list[str] = []
        for f in self._meta.concrete_fields:
            name = f.attname
            before = initial.get(name, None)
            now = _value_for_compare(getattr(self, name))
            if before != now:
                changed.append(
                    f.name
                )  # use logical field name (not attname) for clarity
        return changed

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

        self._capture_initial_state()


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
