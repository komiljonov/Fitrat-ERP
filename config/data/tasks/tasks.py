import os
import logging
from datetime import datetime

from celery import shared_task
from root.celery import app


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

