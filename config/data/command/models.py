from typing import TYPE_CHECKING
from uuid import uuid4

from django.db import models
from django.utils import timezone

from django.db.models.fields.files import FieldFile

from django.db.models import Q, CheckConstraint


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


_SENTINEL = object()


class BaseModel(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)

    filial: "Filial | None" = models.ForeignKey(
        "filial.Filial",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    is_archived = models.BooleanField(default=False)
    archived_at = models.BooleanField(null=True, blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    # New: creation/update call-site snapshots
    create_context = models.JSONField(null=True, blank=True)
    update_context = models.JSONField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]

        constraints = [
            CheckConstraint(
                name="%(app_label)s_%(class)s_arch_ts_chk",
                condition=Q(is_archived=False) | Q(archived_at__isnull=False),
            )
        ]

    # ---------- change tracking ----------
    def _capture_initial_state_from_dict(self):
        """
        Snapshot using raw __dict__ (never triggers DB loads for deferred attrs).
        Only records fields that already exist in __dict__.
        """
        self.__initial_state__ = {}
        for f in self._meta.concrete_fields:
            raw = self.__dict__.get(f.attname, _SENTINEL)
            if raw is _SENTINEL:
                # field is deferred/not populated; skip to avoid DB hits
                continue
            self.__initial_state__[f.attname] = _value_for_compare(raw)

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Called when instantiating from the DB. We can build the snapshot directly
        from (field_names, values) without touching descriptors.
        """
        instance = super().from_db(db, field_names, values)
        state = {}
        # field_names may be None (select *), so fallback to model fields
        if field_names is None:
            # When None, values align with all concrete fields in their definition order
            for f, v in zip(instance._meta.concrete_fields, values):
                state[f.attname] = _value_for_compare(v)
        else:
            name_to_val = dict(zip(field_names, values))
            for f in instance._meta.concrete_fields:
                if f.attname in name_to_val:
                    state[f.attname] = _value_for_compare(name_to_val[f.attname])
                elif f.name in name_to_val:
                    state[f.attname] = _value_for_compare(name_to_val[f.name])
                # else: field deferred → leave it out to avoid DB load
        instance.__initial_state__ = state
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # After constructing (even new objects), capture initial state.
        self._capture_initial_state_from_dict()

    def changed_fields(self) -> list[str]:
        """
        Compare current raw values vs initial snapshot. Uses __dict__ to avoid
        triggering deferred loads. If a field wasn't in the initial snapshot
        (deferred at load time) but is now present, we consider it "changed".
        """
        initial = getattr(self, "__initial_state__", {}) or {}
        changed: list[str] = []
        for f in self._meta.concrete_fields:
            att = f.attname
            before = initial.get(att, _SENTINEL)
            now_raw = self.__dict__.get(att, _SENTINEL)
            # Normalize (but only if present)
            now = _value_for_compare(now_raw) if now_raw is not _SENTINEL else _SENTINEL
            if before is _SENTINEL and now is _SENTINEL:
                continue  # both absent (still deferred)
            if before is _SENTINEL and now is not _SENTINEL:
                changed.append(f.name)  # newly populated → treat as changed
            elif before != now:
                changed.append(f.name)
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

        self._capture_initial_state_from_dict()


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
