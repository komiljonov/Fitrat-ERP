import logging
from datetime import datetime
from celery import shared_task
from django.utils.timezone import now
from .models import Employee_attendance

logging.basicConfig(level=logging.INFO)

@shared_task
def check_daily_user_attendance():
    """
    This task runs daily at 00:00 and marks all employees
    who didn't attend as 'not_attended'.
    """
    # Get all employees who haven't attended today
    today = now().date()
    unattended_users = Employee_attendance.objects.filter(date=today,
                                                          action__not_in=["In_office", "Absent"],
                                                          ).all()
    for user in unattended_users:
        Employee_attendance.objects.create(
            user=user.user,
            action="Gone",
            date=today,
            time=datetime.now())

    logging.info(f"Updated {unattended_users.count()} users as 'not_attended'.")
