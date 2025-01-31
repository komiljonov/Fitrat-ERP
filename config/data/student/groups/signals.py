from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import Group
from ...notifications.models import Notification


@receiver(post_save, sender=Group)
def on_create(sender, instance: Group, created, **kwargs):
    if created:
        pass


