import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import Employee_attendance, UserTimeLine
from .utils import calculate_penalty
from ...account.models import CustomUser


@receiver(post_save, sender=Employee_attendance)
def on_create(sender, instance: Employee_attendance, created, **kwargs):
    if created:
        day_name = instance.check_in.strftime('%A') if instance.check_in else None

        if instance.check_in and not instance.check_out:
            timeline_qs = UserTimeLine.objects.filter(user=instance.employee, day=day_name)
            if timeline_qs.exists():
                time_entry = timeline_qs.first()
                scheduled_time = time_entry.start_time

                if scheduled_time < instance.check_in.time():
                    instance.status = "Late"
                else:
                    instance.status = "On_time"
                instance.save()

        if instance.check_out and instance.check_in:
            pair = Employee_attendance.objects.filter(
                employee=instance.employee,
                status="Late",
                check_in=instance.check_in
            )
            if pair:
                penalty = calculate_penalty(
                    check_in=instance.check_in,
                    check_out=instance.check_out,
                    user_id=instance.employee.id
                )
                ic(pair,penalty)
                instance.amount = penalty
                instance.save()
                instance.status = "Gone"
                instance.save()



