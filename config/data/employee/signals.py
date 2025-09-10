from django.dispatch import receiver

from django.db.models.signals import post_save

from config.data.logs.models import Log
from data.employee.models import EmployeeTransaction


@receiver(post_save, sender=EmployeeTransaction)
def on_employee_transaction_created(
    sender, instance: EmployeeTransaction, created, **kwargs
):

    # Only run on create
    if not created:
        return

    # Do your logic here
    # Example: update employee balance
    employee = instance.employee

    employee.balance += instance.effective_amount

    employee.save(update_fields=["balance"])

    Log.objects.create(
        object="EMPLOYEE",
        action="TRANSACTION_CREATED",
        employee_transaction=instance,
        employee=instance.employee,
        comment=f"Transaction created for employee {employee.full_name}.",
    )
