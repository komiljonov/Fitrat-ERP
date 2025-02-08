import logging
from datetime import timedelta
from celery import shared_task
from django.utils.timezone import now
from .models import Lid
from ...notifications.models import Notification

logging.basicConfig(level=logging.INFO)

@shared_task
def check_daily_leads():
    overdue_lead = Lid.objects.filter(
        is_archived=False,
        updated_at__lte=now() - timedelta(days=3),
    )
    for task in overdue_lead:
        if task.lid_stage_type == "NEW_LID" or task.is_expired:
            task.is_expired = "O'TIB_KETGAN"
            task.save()
            logging.info(f"Lead {task.id} stage updated to 'O'TIB_KETGAN'.")

        if task.call_operator:
            Notification.objects.create(
                user=task.call_operator,
                comment=f"Lead {task.first_name} {task.last_name} - {task.phone_number} bilan aloqa bo'lmaganiga 3 kun bo'ldi!",
                come_from=task
            )
            logging.info(f"Notification created for lead {task.id}.")
        else:
            logging.warning(f"No call operator assigned to lead {task.id}. Notification skipped.")

    logging.info("Celery task completed: Checked daily leads.")
