from celery import shared_task

from data.employee.models import Employee


@shared_task
def bonuses_for_each_active_student():

    employees = Employee.objects.filter(is_archived=False)

    for employee in employees:

        employee.calculate_monthly_salary()
