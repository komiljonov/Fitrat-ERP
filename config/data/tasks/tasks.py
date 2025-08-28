from django.utils import timezone
import logging
from celery import shared_task
from .models import Task
from data.notifications.models import Notification

logger = logging.getLogger(__name__)


@shared_task
def check_daily_tasks():
    now = timezone.now()

    overdue_tasks = Task.objects.filter(status="ONGOING", date_of_expired__lte=now)

    for task in overdue_tasks:
        task.status = "EXPIRED"
        task.save()

        Notification.objects.create(
            user=task.creator,
            comment=f"You have an expired task.\nComment: {task.comment or 'No comment'}",
            come_from=task.id,
            choice="Tasks",
        )
        logger.info(
            f"Task {task.id} marked as EXPIRED and notification sent to user {task.creator_id}"
        )

    logger.info("Completed checking daily tasks for expiration.")


@shared_task
def check_today_tasks():
    today = timezone.localdate()

    tasks = Task.objects.filter(status="SOON", date_of_expired__date=today)

    for task in tasks:
        task.status = "ONGOING"
        task.save()
        logger.info(f"Task {task.id} scheduled for today marked as ONGOING.")
