from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError


from django.db.models.signals import pre_save, post_save, post_delete

from data.logs.models import Log
from data.employee.models import EmployeeTransaction


@receiver(pre_save, sender=EmployeeTransaction)
def before_employee_transaction_creating(sender, instance, **kwargs):

    print("AAA", instance.reason)

    if instance.reason in EmployeeTransaction.REASON_TO_ACTION:
        instance.action = EmployeeTransaction.REASON_TO_ACTION[instance.reason]
        print(instance.action)
    else:
        raise ValidationError(
            f"Invalid reason '{instance.reason}' for EmployeeTransaction"
        )


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
                f"Transaction created for employee {employee.full_name}. {f'By {instance.created_by.full_name}({instance.created_by.phone})' if instance.created_by else "-"}, "
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
            # employee_transaction=instance,
            employee=employee,
            comment=(
                f"Transaction deleted for employee {employee.full_name}. {f'By {instance.created_by.full_name}({instance.created_by.phone})' if instance.created_by else "-"}, "
                f"Start: {start_balance}, Change: -{instance.effective_amount}, "
                f"Final: {final_balance}."
            ),
        )
