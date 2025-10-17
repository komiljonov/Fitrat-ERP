from typing import TYPE_CHECKING
from django.db import models, transaction

from data.command.models import BaseModel

if TYPE_CHECKING:
    from data.student.student.models import Student
    from data.lid.new_lid.models import Lid
    from data.employee.models import Employee
    from data.logs.models import Log

# Create your models here.


class StudentTransaction(BaseModel):

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

    REASON_TO_ACTION = {
        # Income and incomes
        "BONUS": INCOME,
        "FINE": EXPENSE,
        "COURSE_PAYMENT": INCOME
    }

    REASON_TO_TEXT = {
        "BONUS": "Bonus",
        "FINE": "Jarima",
    }

    reason = models.CharField(
        max_length=255,
        choices=[
            ("BONUS", "Bonus"),
            ("FINE", "Fine"),
            ("COURSE_PAYMENT", "Course Payment"),
        ],
    )

    action = models.CharField(
        choices=[
            (INCOME, "Kirim"),
            (EXPENSE, "Chiqim"),
        ],
    )

    student: "Student | None" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_transactions",
        help_text="Field for referencing student in Employee transactions, for something like course_payment or other things.",
    )

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_transactions",
    )

    amount = models.DecimalField(decimal_places=2, max_digits=12)

    effective_amount = models.DecimalField(decimal_places=2, max_digits=12)

    comment = models.TextField(null=True, blank=True)

    created_by: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_student_transactions"
    )

    def save(self, *args, **kwargs):

        print(self.action, self.amount)

        # Apply business rule before saving
        if self.action == "INCOME":
            self.effective_amount = self.amount

        elif self.action == "EXPENSE":
            self.effective_amount = -self.amount

        else:
            self.effective_amount = self.amount  # fallback

        super().save(*args, **kwargs)
        print("SAVED Effective amount")


    def cancel(self, comment: str | None = None):

        with transaction.atomic():

            start_balance = self.employee.balance
            final_balance = start_balance - self.effective_amount

            # Update balance
            self.employee.balance = final_balance
            self.employee.save(update_fields=["balance"])

            # Log deletion
            Log.objects.create(
                object="STUDENT",
                action="TRANSACTION_DELETED",
                employee_transaction=self,
                employee=self.employee,
                comment=(
                    f"Transaction archived for student or lead {self.employee.full_name}. "
                    f"Start: {start_balance}, Change: -{self.effective_amount}, "
                    f"Final: {final_balance}. Comment: {comment}"
                ),
            )

            self.is_archived = True
            self.set_archived_at()
            self.save()
            print("LOG WORKED")