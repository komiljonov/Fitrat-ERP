from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import MasteringTeachers
from ...notifications.models import Notification


@receiver(post_save, sender=MasteringTeachers)
def on_create(sender, instance: MasteringTeachers, created, **kwargs):
    if created:
        pass

