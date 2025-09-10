from django.db import models

from config.data.command.models import BaseModel
from data.account.models import CustomUser
from data.employee.manager import EmployeeManager


# Create your models here.


class Employee(CustomUser):

    objects = EmployeeManager()

    class Meta:
        proxy = True


class EmployeeTransaction(BaseModel):

    employee: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    reason = models.CharField(
        max_length=255, choices=[("BONUS", "Bonus"), ("FINE", "Fine")]
    )

    amount = models.DecimalField(decimal_places=2, max_digits=12)

    effective_amount = models.DecimalField(decimal_places=2, max_digits=12)

    def save(self, *args, **kwargs):
        # Apply business rule before saving
        if self.reason == "BONUS":
            self.effective_amount = self.amount
        elif self.reason == "FINE":
            self.effective_amount = -self.amount
        else:
            self.effective_amount = self.amount  # fallback

        super().save(*args, **kwargs)
