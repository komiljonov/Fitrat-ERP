from datetime import datetime

from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from data.finances.timetracker.models import UserTimeLine, Employee_attendance
from data.student.studentgroup.models import StudentGroup
from .models import Stuff_Attendance

UZBEK_WEEKDAYS = {
    'Dushanba': 0, 'Seshanba': 1, 'Chorshanba': 2,
    'Payshanba': 3, 'Juma': 4, 'Shanba': 5, 'Yakshanba': 6
}


@receiver(post_save, sender=Stuff_Attendance)
def on_create(sender, instance: Stuff_Attendance, created, **kwargs):
    if not created or not instance.check_in:
        return

    today = instance.check_in.date()
    today_weekday = today.weekday()
    day_name = today.strftime('%A')

    user = instance.employee
    if not user:
        return

    if user.calculate_penalties and user.role in {"TEACHER", "ASSISTANT"}:

        student_groups = StudentGroup.objects.filter(
            Q(group__teacher=user) | Q(group__secondary_teacher=user)
        ).select_related('group').prefetch_related('group__scheduled_day_type')

        for sg in student_groups:
            group = sg.group
            if not group or not group.started_at:
                continue

            scheduled_days = group.scheduled_day_type.values_list('name', flat=True)
            scheduled_indexes = {
                UZBEK_WEEKDAYS[day] for day in scheduled_days if day in UZBEK_WEEKDAYS
            }

            if today_weekday in scheduled_indexes:
                dt = datetime.combine(today, group.started_at)
                if timezone.is_naive(dt):
                    dt = timezone.make_aware(dt)
                group_start_dt = dt
                if instance.check_in > group_start_dt:
                    instance.status = "Late"
                else:
                    instance.status = "On_time"
                instance.save()
                return

    else:
        timeline = UserTimeLine.objects.filter(user=user, day=day_name).first()
        if timeline:
            scheduled_time = datetime.combine(today, timeline.start_time)
            if instance.check_in > scheduled_time:
                instance.status = "Late"
            else:
                instance.status = "On_time"
            instance.save()



is_updating_status = False  # global flag

@receiver(post_save, sender=Employee_attendance)
def on_create(sender, instance: Employee_attendance, created, **kwargs):
    global is_updating_status

    if created or is_updating_status:
        return

    last_att = instance.attendance.first()
    new_status = None

    if last_att and last_att.check_out:
        new_status = "Gone"
    elif last_att and last_att.check_in and last_att.check_out is None:
        new_status = "In_office"

    if new_status and instance.status != new_status:
        is_updating_status = True
        instance.status = new_status
        instance.save(update_fields=["status"])
        is_updating_status = False