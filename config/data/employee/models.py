from typing import TYPE_CHECKING

from django.db import models
from django.contrib import admin

from data.account.models import CustomUser
from data.employee.manager import EmployeeManager

if TYPE_CHECKING:
    from data.archive.models import Archive
    from data.student.student.models import Student

from data.employee.methods import EmployeeMethods

# Don't remove, it must apply as model in this app.
from data.employee.transactions.models import EmployeeTransaction
from data.employee.finance import FinanceManagerKpi


# Create your models here.


class Employee(CustomUser, EmployeeMethods):

    objects = EmployeeManager()

    archives: "models.QuerySet[Archive]"
    unarchives: "models.QuerySet[Archive]"
    transactions: "models.QuerySet[EmployeeTransaction]"

    # Service manager bo'yicha o'quvchilar
    svm_students: "models.QuerySet[Student]"

    finance_manager_kpis: "models.QuerySet[FinanceManagerKpi]"
    
    

    class Meta:
        proxy = True

    class Admin(admin.ModelAdmin):

        list_display = ["id", "full_name", "phone", "role", "balance"]

        list_filter = ["is_archived", "filial", "role"]
