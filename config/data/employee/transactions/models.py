from typing import TYPE_CHECKING
from django.db import models
from django.contrib import admin


from data.command.models import BaseModel
from data.firstlesson.models import FirstLesson

if TYPE_CHECKING:
    from data.student.lesson.models import FirstLLesson
    from data.student.student.models import Student
    from data.employee.models import Employee
    from data.lid.new_lid.models import Lid
    from data.finances.finance.models import Finance


class EmployeeTransaction(BaseModel):

    INCOME = "INCOME"
    EXPENSE = "EXPENSE"

    REASON_TO_ACTION = {
        "BONUS": INCOME,
        "FINE": EXPENSE,
        "BONUS_FOR_FIRST_LESSON": INCOME,
        "SALARY": INCOME,
        "ADVANCE": EXPENSE,
    }

    employee: "Employee" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    reason = models.CharField(
        max_length=255,
        choices=[
            ("BONUS", "Bonus"),
            ("FINE", "Fine"),
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
        related_name="student_employee_transaction",
        help_text="Field for referencing student in Employee transactions, for something like course_payment or other things.",
    )

    old_first_lesson: "FirstLLesson | None" = models.ForeignKey(
        "lesson.FirstLLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_transactions",
        help_text="Field for referencing student in Employee transactions, for something like ",
    )

    first_lesson_new: "FirstLesson | None" = models.ForeignKey(
        "firstlesson.FirstLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_transactions",
    )

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_transactions",
    )

    finance: "Finance | None" = models.ForeignKey(
        "finance.Finance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employee_transactions",
    )

    amount = models.DecimalField(decimal_places=2, max_digits=12)

    effective_amount = models.DecimalField(decimal_places=2, max_digits=12)

    comment = models.TextField(null=True, blank=True)

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
