from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Student, Archived
from ...notifications.models import Notification


@receiver(post_save, sender=Archived)
def on_create(sender, instance: Archived, created, **kwargs):
    if created:
        if instance.student:
            instance.student.is_archived = True
            instance.student.save()

        if instance.lid:
            instance.lid.is_archived = True
            instance.lid.save()

