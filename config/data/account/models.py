from typing import TYPE_CHECKING
import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from data.command.utils import capture_context_deep
from data.department.filial.models import Filial
from data.account.managers import UserManager
from data.upload.models import File

if TYPE_CHECKING:
    from data.notifications.models import Notification


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


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    username = None

    files: "File" = models.ManyToManyField(
        "upload.File",
        blank=True,
        related_name="account_files",
    )

    second_user = models.CharField(max_length=100, unique=True, null=True, blank=True)

    full_name = models.CharField(max_length=100, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)

    last_name = models.CharField(max_length=100, blank=True, null=True)

    phone = models.CharField(max_length=255, unique=True, blank=True, null=True)

    extra_number = models.CharField(max_length=255, blank=True, null=True)

    chat_id = models.CharField(max_length=255, blank=True, null=True)

    calculate_penalties = models.BooleanField(default=False)

    calculate_bonus = models.BooleanField(default=False)

    photo: "File" = models.ForeignKey(
        "upload.File",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField(blank=True, null=True)

    ROLE_CHOICES = (
        ("CALL_OPERATOR", "Call Center"),
        ("ADMINISTRATOR", "Sales Menejeri"),
        ("SERVICE_MANAGER", "Service Manager"),
        ("CALL_SALES", "Call Sales"),
        ("SERVICE_SALES", "Service Sales"),
        ("ACCOUNTING", "Accounting"),
        ("ATTENDANCE_MANAGER", "Attendance Manager"),
        ("FILIAL_Manager", "Filial Manager"),
        ("HEAD_TEACHER", "Head Teacher"),
        ("MONITORING_MANAGER", "Monitoring Manager"),
        ("TESTOLOG", "Testolog"),
        ("TEACHER", "Teacher"),
        ("ASSISTANT", "Assistant teacher"),
        ("MULTIPLE_FILIAL_MANAGER", "Multiple Filial Manager"),
        ("DIRECTOR", "Director"),
        ("Student", "Student"),
        ("Parents", "Parents"),
    )

    is_call_center = models.BooleanField(default=False)

    role = models.CharField(choices=ROLE_CHOICES, max_length=30, default="DIRECTOR")

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00"),
    )

    salary = models.FloatField(default=0)

    ball = models.FloatField(default=0)

    monitoring = models.FloatField(default=0)

    enter = models.TimeField(null=True, blank=True)

    leave = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    filial: "models.ManyToManyField[Filial]" = models.ManyToManyField(
        "filial.Filial",
        blank=True,
        related_name="users_filials",
    )

    is_archived = models.BooleanField(default=False)

    create_context = models.JSONField(null=True, blank=True)
    update_context = models.JSONField(null=True, blank=True)

    USERNAME_FIELD = "phone"
    # REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    notifications: "models.QuerySet[Notification]"

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return str(self.full_name or self.phone)

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
