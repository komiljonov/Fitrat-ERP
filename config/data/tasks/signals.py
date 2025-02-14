import datetime

from django.db.models.signals import post_save
from django.dispatch import receiver

from data.tasks.models import Task


@receiver(post_save, sender=Task)
def on_create(sender, instance: Task, created, **kwargs):
    if created:
        # Get the current time
        current_time = datetime.datetime.now()

        # Check if the expiration date is in the future or the past
        if instance.date_of_expired > current_time:
            instance.status = "SOON"
        else:
            instance.status = "EXPIRED"

        # Save the status change to the task
        instance.save(update_fields=["status"])
