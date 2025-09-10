from django.contrib import admin

from data.employee.models import Employee


# Register your models here.


@admin.register(Employee)
class Admin(admin.ModelAdmin):

    list_display = ["id", "full_name", "phone", "role", "balance", "filial"]

    list_filter = ["filial", "role"]
