import datetime
import logging

from celery import shared_task

from .models import Student

@shared_task
def update_frozen_status():
    frozen_days = Student.objects.filter(is_frozen=True,frozen_days__isnull=False).all()
    for day in frozen_days:
        if day.frozen_days == datetime.datetime.today():
            day.is_frozen = False
            day.frozen_days = None
            day.save()
            logging.info("Frozen days updated")