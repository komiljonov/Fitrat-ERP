import uuid
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

from data.department.filial.models import Filial
from ..account.managers import UserManager
from ..upload.models import File


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    files: 'File' = models.ManyToManyField('upload.File', blank=True, related_name='account_files')

    second_user = models.CharField(max_length=100, unique=True, null=True, blank=True)

    full_name = models.CharField(max_length=100, blank=True, null=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)

    last_name = models.CharField(max_length=100, blank=True, null=True)

    phone = models.CharField(max_length=255, unique=True, blank=True, null=True)

    extra_number = models.CharField(max_length=255, blank=True, null=True)

    chat_id = models.CharField(max_length=255, blank=True, null=True)

    calculate_penalties = models.BooleanField(default=False)

    calculate_bonus = models.BooleanField(default=False)

    photo: 'File' = models.ForeignKey('upload.File', on_delete=models.SET_NULL, blank=True, null=True)

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

    balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    salary = models.FloatField(default=0)

    ball = models.FloatField(default=0)

    monitoring = models.FloatField(default=0)

    enter = models.TimeField(null=True, blank=True)

    leave = models.TimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    filial: 'Filial' = models.ManyToManyField('filial.Filial', blank=True, related_name='users_filials')

    is_archived = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    # REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.full_name or self.phone
