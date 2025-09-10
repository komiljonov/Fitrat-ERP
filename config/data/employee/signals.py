from django.dispatch import receiver
from django.db import transaction

from django.db.models.signals import post_save, post_delete

from data.logs.models import Log
from data.employee.models import EmployeeTransaction


@receiver(post_save, sender=EmployeeTransaction)
def on_employee_transaction_created(
    sender, instance: EmployeeTransaction, created, **kwargs
):
    if not created:
        return

    employee = instance.employee

    with transaction.atomic():
        start_balance = employee.balance
        final_balance = start_balance + instance.effective_amount

        # Update balance
        employee.balance = final_balance
        employee.save(update_fields=["balance"])

        # Log creation
        Log.objects.create(
            object="EMPLOYEE",
            action="TRANSACTION_CREATED",
            employee_transaction=instance,
            employee=employee,
            comment=(
                f"Transaction created for employee {employee.full_name}. "
                f"Start: {start_balance}, Change: +{instance.effective_amount}, "
                f"Final: {final_balance}."
            ),
        )


@receiver(post_delete, sender=EmployeeTransaction)
def on_transaction_deleted(sender, instance: EmployeeTransaction, **kwargs):
    employee = instance.employee

    with transaction.atomic():
        start_balance = employee.balance
        final_balance = start_balance - instance.effective_amount

        # Update balance
        employee.balance = final_balance
        employee.save(update_fields=["balance"])

        # Log deletion
        Log.objects.create(
            object="EMPLOYEE",
            action="TRANSACTION_DELETED",
            employee_transaction=instance,
            employee=employee,
            comment=(
                f"Transaction deleted for employee {employee.full_name}. "
                f"Start: {start_balance}, Change: -{instance.effective_amount}, "
                f"Final: {final_balance}."
            ),
        )
