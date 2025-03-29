import logging
from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from .models import Group
from ..lesson.models import ExtraLesson
from ..studentgroup.models import StudentGroup
from ...account.models import CustomUser
from ...finances.finance.models import KpiFinance
from ...notifications.models import Notification

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
                user=[user for user in CustomUser.objects.filter(
                    role__in=["SERVICE_MANAGER","DIRECTOR","ASSISTANT"])],
                comment=f"{group.name} nomli guruh bugun faollashtirildi !",
                come_from=group,
            )
        logging.info("Activate group {}".format(group))

