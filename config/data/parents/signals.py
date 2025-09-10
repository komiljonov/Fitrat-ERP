from django.db.models.signals import post_save
from django.dispatch import receiver

from data.logs.models import Log

from .models import Relatives


@receiver(post_save, sender=Relatives)
def on_create(sender, instance: Relatives, created, **kwargs):
    if created:
        Log.objects.create(
            object="STUDENT" if instance.student else "LEAD",
            action="RELATIVE_CREATED",
            lead=instance.lid,
            student=instance.student,
        )
    if not created:
        Log.objects.create(
            object="STUDENT" if instance.student else "LEAD",
            action="RELATIVE_UPDATED",
            lead=instance.lid,
            student=instance.student,
        )
