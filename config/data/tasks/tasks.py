import logging
from datetime import datetime, date

from celery import shared_task

from .models import Task
from ..notifications.models import Notification

logging.basicConfig(level=logging.INFO)

@shared_task
def check_daily_tasks():

    overdue_tasks = Task.objects.filter(
        status="ONGOING",
        date_of_expired__lte=datetime.now()
    )
    for task in overdue_tasks:
        task.status = "EXPIRED"
        task.save()
        notification_tasks = Notification.objects.create(
            user=task.creator,
            comment=f"You got a expired task \n Task comment : {task.comment}",
            come_from=task
        )
        if notification_tasks:
            logging.info("For task notification created !")

    logging.info("Celery task completed: Checked daily tasks.")


@shared_task
def check_today_tasks():
    today = date.today()
    tasks = Task.objects.filter(status="SOON", date_of_expired__date=today)

    for task in tasks:
        task.status = "ONGOING"
        task.save()
        logging.info(f"Task {task.id} status changed to ONGOING for today.")