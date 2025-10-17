from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError


from django.db.models.signals import pre_save, post_save, post_delete

from data.logs.models import Log
from data.student.transactions.models import StudentTransaction


@receiver(pre_save, sender=StudentTransaction)
def before_student_transaction_creating(sender, instance: StudentTransaction, **kwargs):
    print("Before Trigger worked")

    if instance.reason in StudentTransaction.REASON_TO_ACTION:
        instance.action = StudentTransaction.REASON_TO_ACTION[instance.reason]
        print(instance.action)
    else:
        raise ValidationError(
            f"Invalid reason '{instance.reason}' for StudentTransaction"
        )


@receiver(post_save, sender=StudentTransaction)
def on_student_transaction_created(
    sender, instance: StudentTransaction, created, **kwargs
):
    print("Post Save Trigger worked")
    if not created:
        return

    student = instance.student

    with transaction.atomic():
        start_balance = student.balance
        final_balance = start_balance + instance.effective_amount

        # Update balance
        student.balance = final_balance
        student.save(update_fields=["balance"])

        # Log creation
        Log.objects.create(
            object="STUDENT",
            action="TRANSACTION_CREATED",
            student_transaction=instance,
            student=student,
            comment=(
                f"Transaction created for student {student.first_name} {student.last_name}. {f'By {instance.created_by.full_name}({instance.created_by.phone})' if instance.created_by else "-"}, "
                f"Start: {start_balance}, Change: +{instance.effective_amount}, "
                f"Final: {final_balance}."
            ),
        )


@receiver(post_delete, sender=StudentTransaction)
def on_transaction_deleted(sender, instance: StudentTransaction, **kwargs):
    print("POST DELETE Trigger worked")
    student = instance.student

    with transaction.atomic():
        start_balance = student.balance
        final_balance = start_balance - instance.effective_amount

        # Update balance
        student.balance = final_balance
        student.save(update_fields=["balance"])

        # Log deletion
        Log.objects.create(
            object="STUDENT",
            action="TRANSACTION_DELETED",
            # student_transaction=instance,
            student=student,
            comment=(
                f"Transaction deleted for student {student.first_name} {student.last_name}. {f'By {instance.created_by.full_name}({instance.created_by.phone})' if instance.created_by else "-"}, "
                f"Start: {start_balance}, Change: -{instance.effective_amount}, "
                f"Final: {final_balance}."
            ),
        )
