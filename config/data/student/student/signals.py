from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from ...account.models import CustomUser
from ...notifications.models import Notification

# Define a flag to prevent recursion
_signal_active = False

@receiver(post_save, sender=Student)
def on_create(sender, instance: Student, created, **kwargs):
    global _signal_active

    if _signal_active:
        return

    if not created:
        try:
            _signal_active = True  #Set the flag to prevent recursion
            if instance.new_student_date == None and instance.student_stage_type == "NEW_STUDENT":
                instance.new_student_date = datetime.now()

            if instance.balance <= 0:
                Notification.objects.create(
                    user=instance.call_operator,
                    comment=f"{instance.first_name} {instance.last_name} ning balance miqdori {instance.balance} sum,"
                            f" to'lov amalga oshirishi haqida eslating!",
                    come_from=instance,
                )
                if instance.balance_status == "ACTIVE":
                    instance.balance_status = "INACTIVE"
                    instance.save(update_fields=["balance_status"])  # Save only the specific field

            elif instance.balance >= 100000:
                instance.balance_status = "ACTIVE"
                instance.student_stage_type = "ACTIVE_STUDENT"
                instance.active_date = datetime.now()
                instance.new_student_stages = None
                instance.save(update_fields=["balance_status","student_stage_type","new_student_stages","active_date"])  # Save only the specific field

        finally:
            _signal_active = False


@receiver(post_save,sender=Student)
def on_create_user(sender, instance: Student, created, **kwargs):
    if created:
        user = CustomUser.objects.create_user(
            first_name=instance.first_name,
            last_name=instance.last_name,
            phone=instance.phone,
            role="Student",
            password=instance.password if instance.password else "1234",
            # filial=instance.filial,
        )
        if user:
            instance.user = user
            instance.save(update_fields=["user"])

