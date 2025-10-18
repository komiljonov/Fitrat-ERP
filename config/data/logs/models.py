from typing import TYPE_CHECKING

from django.db import models

from data.student.transactions.models import StudentTransaction
from data.command.models import BaseModel


from django.contrib import admin


if TYPE_CHECKING:
    from data.tasks.models import Task
    from data.student.student.models import Student
    from data.student.lesson.models import FirstLLesson
    from data.results.models import Results
    from data.finances.finance.models import Finance
    from data.lid.archived.models import Archived, Frozen
    from data.lid.new_lid.models import Lid
    from data.account.models import CustomUser
    from data.employee.models import Employee
    from data.employee.models import EmployeeTransaction
    from data.student.studentgroup.models import StudentGroup


class Log(BaseModel):

    object = models.CharField(
        max_length=255,
        choices=[
            ("LEAD", "Lead"),
            ("STUDENT", "Student"),
            ("EMPLOYEE", "Employee"),
        ],
    )

    action = models.CharField(
        choices=[
            ("Finance", "Finance"),
            ("Log", "Log"),
            ("CreateTransaction", "CreateTransaction"),
            ("ARCHIVE_STUDENT_GROUP", "O'quvchi guruhi archivelandi."),
        ],
        max_length=255,
        null=True,
        blank=True,
    )

    # model_action = models.CharField(
    #     choices=[
    #         ("Created", "Created"),
    #         ("Updated", "Updated"),
    #         ("Deleted", "Deleted"),
    #         ("Archived", "Archived"),
    #         ("Unarchived", "Unarchived"),
    #     ],
    #     max_length=255,
    #     null=True,
    #     blank=True,
    # )

    # Objectives

    finance: "Finance" = models.ForeignKey(
        "finance.Finance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_finances",
    )

    lead: "Lid | None" = models.ForeignKey(
        "new_lid.Lid",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_lids",
    )

    first_lessons: "FirstLLesson" = models.ForeignKey(
        "lesson.FirstLLesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_first_lessons",
    )

    student: "Student" = models.ForeignKey(
        "student.Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_students",
    )

    archive: "Archived" = models.ForeignKey(
        "archived.Archived",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_archives",
    )

    account: "CustomUser" = models.ForeignKey(
        "account.CustomUser",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_customuser",
    )

    result: "Results" = models.ForeignKey(
        "results.Results",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_results",
    )

    task: "Task" = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="log_tasks",
    )

    frozen: "Frozen | None" = models.ForeignKey(
        "archived.Frozen",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    employee: "Employee | None" = models.ForeignKey(
        "employee.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    employee_transaction: "EmployeeTransaction | None" = models.ForeignKey(
        "employee.EmployeeTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )
    student_transaction: "StudentTransaction | None" = models.ForeignKey(
        "transactions.StudentTransaction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    student_group: "StudentGroup | None" = models.ForeignKey(
        "studentgroup.StudentGroup",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logs",
    )

    comment = models.TextField(null=True, blank=True)

    class Admin(admin.ModelAdmin):

        list_display = ["id", "object", "action_raw", "action", "created_at"]

        list_filter = [
            "object",
            "action",
        ]

        def action_raw(self, obj):

            return obj.action

        action_raw.short_description = "Action (Raw)"
