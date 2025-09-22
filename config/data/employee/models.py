from django.db import models
from django.contrib import admin

from data.account.models import CustomUser
from data.archive.models import Archive
from data.employee.manager import EmployeeManager


# Don't remove, it must apply as model in this app.
from data.employee.transactions.models import EmployeeTransaction

# Create your models here.


class Employee(CustomUser):

    objects = EmployeeManager()

    archives: "models.QuerySet[Archive]"
    unarchives: "models.QuerySet[Archive]"
    transactions: "models.QuerySet[EmployeeTransaction]"

    class Meta:
        proxy = True

    class Admin(admin.ModelAdmin):

        list_display = ["id", "full_name", "phone", "role", "balance"]

        list_filter = ["filial", "role"]
