import logging
from datetime import datetime

from celery import shared_task

from data.finances.finance.models import SaleStudent


@shared_task
def check_daily_tasks():

    overdue_sales = SaleStudent.objects.filter(
        expire_date__lte=datetime.now()
    )
    for task in overdue_sales:
        task.sale.status = "EXPIRED"
        task.save()


        logging.info("{sale for student has deleted...}")