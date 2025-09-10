import datetime

from celery import shared_task

from .models import Student


@shared_task
def update_frozen_status():
    frozen_days = Student.objects.filter(
        is_frozen=True,
        frozen_days__isnull=False,
    ).all()

    today = datetime.datetime.today()

    for day in frozen_days:
        if day.frozen_days == today:
            day.is_frozen = False
            day.frozen_days = None
            day.save()
