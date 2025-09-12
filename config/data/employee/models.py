from django.db import models
from django.contrib import admin

from data.command.models import BaseModel
from data.account.models import CustomUser
from data.employee.manager import EmployeeManager


# Create your models here.


class Employee(CustomUser):

    objects = EmployeeManager()

    class Meta:
        proxy = True

    class Admin(admin.ModelAdmin):

        list_display = ["id", "full_name", "phone", "role", "balance"]

        list_filter = ["filial", "role"]
        
        
        


class EmployeeTransaction(BaseModel):

    employee: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    reason = models.CharField(
        max_length=255, choices=[("BONUS", "Bonus"), ("FINE", "Fine")]
    )

    action = models.CharField(
        choices=[("INCOME", "Kirim"), ("EXPENSE", "Chiqim")],
    )

    amount = models.DecimalField(decimal_places=2, max_digits=12)

    effective_amount = models.DecimalField(decimal_places=2, max_digits=12)

    created_by: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    def save(self, *args, **kwargs):
        # Apply business rule before saving
        if self.action == "INCOME":
            self.effective_amount = self.amount

        elif self.action == "EXPENSE":
            self.effective_amount = -self.amount

        else:
            self.effective_amount = self.amount  # fallback

        super().save(*args, **kwargs)

    class Admin(admin.ModelAdmin):

        list_display = ["employee", "reason", "amount", "effective_amount"]

        readonly_fields = ["effective_amount"]
