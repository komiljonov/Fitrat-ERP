import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Employee_attendance, UserTimeLine
from .utils import calculate_penalty
from ...account.models import CustomUser


@receiver(post_save, sender=Employee_attendance)
def on_create(sender, instance: Employee_attendance, created, **kwargs):
    if created:
        if instance.check_in and instance.check_out is None:
            timeline = UserTimeLine.objects.filter(user=instance.employee)
            if timeline:
                for time in timeline:
                    day_name = datetime.datetime.today().strftime('%A')
                    print(day_name)

                    if time.day == day_name and time.start_time < instance.check_in:
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
                instance.amount = penalty
                instance.status = "Gone"
                instance.save()



