import datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Employee_attendance, UserTimeLine


@receiver(pre_save, sender=Employee_attendance)
def on_update(sender, instance: Employee_attendance, **kwargs):
    if instance.check_in and instance.check_out is None:
        day_name = datetime.datetime.today().strftime('%A')
        try:
            timeline = UserTimeLine.objects.get(user=instance.employee, day=day_name)
            if timeline.start_time and instance.check_in > timeline.start_time:
                instance.status = "Late"
            else:
                instance.status = "On_time"
        except UserTimeLine.DoesNotExist:
            pass  # optionally log or handle missing timeline
        # elif instance.check_in and instance.check_out:
        #     pair = get_object_or_404(
        #         Employee_attendance,
        #         check_in=instance.check_in,
        #     )
        #     if pair.check_out is None :
        #         pair.check_out = instance.check_out
        #         pair.save()
        #
        #         instance.is_merged = True
        #         instance.save()
