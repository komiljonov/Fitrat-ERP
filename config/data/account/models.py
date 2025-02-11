import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models

from data.department.filial.models import Filial
from ..account.managers import UserManager
from ..finances.compensation.models import Compensation, Bonus, Page
from ..upload.models import File


class CustomUser(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    full_name = models.CharField(max_length=100, blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=255, unique=True, blank=True, null=True)

    photo : File = models.ForeignKey('upload.File', on_delete=models.SET_NULL, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)

    ROLE_CHOICES = (
        ("CALL_OPERATOR", "Call Center"),
        ("ADMINISTRATOR", "Sotuv Menejeri"),
        ("SERVICE_MANAGER", "Service Manager"),
        ("ACCOUNTING", "Accounting"),
        ("ATTENDANCE_MANAGER", "Attendance Manager"),
        ("FILIAL_Manager", "Filial Manager"),
        ("HEAD_TEACHER", "Head Teacher"),
        ("MONITORING_MANAGER", "Monitoring Manager"),
        ("TESTOLOG", "Testolog"),
        ("MODERATOR", "YORDAMCHI USTOZ"),
        ("TEACHER", "Teacher"),
        ("ASSISTANT", "Assistant teacher"),
        ("DIRECTOR", "Director"),
    )
    role = models.CharField(choices=ROLE_CHOICES, max_length=20, default="ADMINISTRATOR")

    balance = models.FloatField(default=0)

    salary = models.FloatField(default=0)

    ball = models.FloatField(default=0)

    enter = models.TimeField(null=True,blank=True)
    leave = models.TimeField(null=True,blank=True)

    created_at = models.DateField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateField(auto_now=True, null=True, blank=True)

    filial : 'Filial' = models.ForeignKey('filial.Filial', on_delete=models.SET_NULL, blank=True, null=True)

    compensation : 'Compensation' = models.ManyToManyField('compensation.Compensation', null=True,blank=True)
    bonus : 'Bonus'= models.ManyToManyField('compensation.Bonus', null=True,blank=True)

    pages : 'Page'= models.ManyToManyField('compensation.Page', null=True, blank=True)

    USERNAME_FIELD = 'phone'
    # REQUIRED_FIELDS = ['phone']

    objects = UserManager()

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.full_name or self.phone




