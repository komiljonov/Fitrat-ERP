import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.generics import get_object_or_404

from .models import Employee_attendance, UserTimeLine
from ...account.models import CustomUser


@receiver(post_save, sender=Employee_attendance)
def on_create(sender, instance: Employee_attendance, created, **kwargs):
    if created:
        if instance.user and instance.action == "In_office":
            user = CustomUser.objects.get(id=instance.user.id)

            # Extract time from datetime
            check_in_time = instance.date.time() if instance.date else None
            expected_time = user.enter.time() if user.enter else None

            if check_in_time and expected_time:
                if check_in_time > expected_time:
                    instance.type = "Late"
                else:
                    instance.type = "On_time"

                instance.save()


@receiver(post_save, sender=Employee_attendance)
def on_update(sender, instance: Employee_attendance, created, **kwargs):
    if created:
        if instance.check_in and instance.check_out is None:

            day_name = datetime.datetime.today().strftime('%A')
            timeline = UserTimeLine.objects.get(user=instance.employee, day=day_name)
            if timeline.start_time and instance.check_in > timeline.start_time:
                instance.status = "Late"
            else:
                instance.status = "On_time"
            instance.save()

        elif instance.check_in and instance.check_out:
            pair = get_object_or_404(
                Employee_attendance,
                check_in=instance.check_in,
            )
            if pair.check_out is None :
                pair.check_out = instance.check_out
                pair.save()

                instance.is_merged = True
                instance.save()

