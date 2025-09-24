from typing import TYPE_CHECKING

from django.db import models
from django.contrib import admin

from data.account.models import CustomUser
from data.employee.manager import EmployeeManager

if TYPE_CHECKING:
    from data.archive.models import Archive


# Don't remove, it must apply as model in this app.
from data.employee.methods import EmployeeMethods
from data.employee.transactions.models import EmployeeTransaction

# Create your models here.


class Employee(CustomUser, EmployeeMethods):

    objects = EmployeeManager()

    archives: "models.QuerySet[Archive]"
    unarchives: "models.QuerySet[Archive]"
    transactions: "models.QuerySet[EmployeeTransaction]"

    class Meta:
        proxy = True

    class Admin(admin.ModelAdmin):

        list_display = ["id", "full_name", "phone", "role", "balance"]

        list_filter = ["filial", "role"]
