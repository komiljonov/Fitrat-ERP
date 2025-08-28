import datetime
import logging

from celery import shared_task
from django.utils.timezone import now

from .models import Group
from data.student.attendance.models import Attendance
from data.account.models import CustomUser
from data.notifications.models import Notification

logging.basicConfig(level=logging.INFO)


@shared_task
def activate_group():
    today = now().date()
    groups = Group.objects.all()
    for group in groups:
        if group.status == "PENDING" and group.start_date == today:
            group.status = "ACTIVE"
            group.save()
            Notification.objects.create(
                user=group.teacher,
                comment=f"{group.name} nomli guruh bugun faollashtirildi !",
                come_from=group,
            )
            Notification.objects.create(
                user=[
                    user
                    for user in CustomUser.objects.filter(
                        role__in=["SERVICE_MANAGER", "DIRECTOR", "ASSISTANT"]
                    )
                ],
                comment=f"{group.name} nomli guruh bugun faollashtirildi !",
                come_from=group,
            )
        logging.info("Activate group {}".format(group))


@shared_task
def attendance_group():
    today = now().date()
    groups = Group.objects.all()
    for group in groups:
        att = Attendance.objects.filter(
            group=group,
            created_at__gte=today,
            created_at__lte=today + datetime.timedelta(days=1),
        )
