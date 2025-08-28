import logging

from celery import shared_task
from django.utils.timezone import now

from .models import Employee_attendance
from ...account.models import CustomUser

logging.basicConfig(level=logging.INFO)

@shared_task
def check_daily_user_attendance():
    """
    This task runs daily at 00:00 and marks all employees
    who didn't attend as 'Gone' if they don't have an 'In_office' record.
    """
    today = now().date()


    all_employees = CustomUser.objects.filter(is_archived=False)


    attended_users = Employee_attendance.objects.filter(
        date=today, action="In_office"
    ).values_list("user", flat=True)


    unattended_users = all_employees.exclude(id__in=attended_users).exclude(
        employee_attendance__date=today, employee_attendance__action="Gone"
    )

    for user in unattended_users:
        Employee_attendance.objects.create(
            user=user,
            action="Gone",
            date=today,
        )

    logging.info(f"📌 Updated {unattended_users.count()} users as 'Gone'.")
