from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Relatives
from ..logs.models import Log


@receiver(post_save, sender=Relatives)
def on_create(sender, instance: Relatives, created, **kwargs):
    if created:
        Log.objects.create(
            app="Parents",
            model="Relatives",
            action="Log",
            model_action="Created",
            lid=instance.lid,
            student=instance.student,
        )
    if not created:
        Log.objects.create(
            app="Parents",
            model="Relatives",
            action="Log",
            model_action="Updated",
            lid=instance.lid,
            student=instance.student,
        )
