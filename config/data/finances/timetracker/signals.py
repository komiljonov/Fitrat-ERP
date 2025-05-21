import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee_attendance
from ...account.models import CustomUser


@receiver(post_save, sender=Employee_attendance)
def on_create(sender, instance: Employee_attendance, created, **kwargs):
    if created:
        if instance.employee and instance.status == "In_office":
            employee = CustomUser.objects.get(id=instance.employee.id)

            # Extract time from datetime
            check_in_time = instance.date.time() if instance.date else None
            expected_time = employee.enter.time() if employee.enter else None

            if check_in_time and expected_time:
                if check_in_time > expected_time:
                    instance.type = "Late"
                else:
                    instance.type = "On_time"

                instance.save()
