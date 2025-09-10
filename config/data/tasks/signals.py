from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from data.logs.models import Log
from data.tasks.models import Task


@receiver(post_save, sender=Task)
def on_create(sender, instance: Task, created, **kwargs):
    if created:
        # Get the current time
        current_time = timezone.now()

        # Check if the expiration date is in the future or the past
        if instance.date_of_expired > current_time:
            instance.status = "SOON"
        else:
            instance.status = "EXPIRED"

        instance.performer.notifications.create(
            comment="Sizda yangi vazifa bor.",
            choice="Tasks",
            come_from="Vazifa yaratilganda keldi.",
        )

        # Save the status change to the task
        instance.save(update_fields=["status"])


@receiver(post_save, sender=Task)
def on_update(sender, instance: Task, created, **kwargs):
    if created:
        Log.objects.create(
            object="TASK",
            action="TASK_CREATED",
            lead=instance.lid,
            student=instance.student,
            task=instance,
            account=instance.performer,
            comment=instance.task,
        )

    if not created:
        Log.objects.create(
            object="TASK",
            action="TASK_UPDATED",
            lead=instance.lid,
            student=instance.student,
            task=instance,
            account=instance.performer,
            comment=instance.task,
        )
