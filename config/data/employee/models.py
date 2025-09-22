from django.db import models
from django.contrib import admin

from data.command.models import BaseModel
from data.account.models import CustomUser
from data.employee.manager import EmployeeManager
from data.finances.finance.models import Finance
from data.lid.new_lid.models import Lid


# Don't remove, it must apply as model in this app.
from data.employee.transactions.models import EmployeeTransaction

# Create your models here.


class Employee(CustomUser):

    objects = EmployeeManager()

    class Meta:
        proxy = True

    class Admin(admin.ModelAdmin):

        list_display = ["id", "full_name", "phone", "role", "balance"]

        list_filter = ["filial", "role"]
