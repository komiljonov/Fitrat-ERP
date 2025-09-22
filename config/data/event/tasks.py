from django.utils import timezone
import logging
from celery import shared_task

from .models import Event

logger = logging.getLogger(__name__)


@shared_task
def check_today_tasks():
    today = timezone.now().date()

    events = Event.objects.filter(end_date__lt=today).exclude(status="Expired")
    if events:
        for event in events:
            event.status = "Expired"
            event.save()
