from datetime import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Student
from ...notifications.models import Notification

# Define a flag to prevent recursion
_signal_active = False

@receiver(post_save, sender=Student)
def on_create(sender, instance: Student, created, **kwargs):
    global _signal_active

    if _signal_active:
        return  # Prevent recursion if the signal is already active

    if not created:
        try:
            _signal_active = True  #Set the flag to prevent recursion
            if instance.new_student_date == None and instance.student_stage_type == "NEW_STUDENT":
                instance.new_student_date = datetime.now()

            if instance.active_date == None and instance.student_stage_type == "ACTIVE_STUDENT":
                instance.active_date = datetime.now()

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

            elif instance.balance > 0:
                instance.balance_status = "ACTIVE"
                instance.student_stage_type = "ACTIVE_STUDENT"
                instance.new_student_stages = None
                instance.save(update_fields=["balance_status","student_stage_type","new_student_stages"])  # Save only the specific field

        finally:
            _signal_active = False  # Reset the flag after processing
