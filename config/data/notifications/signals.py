from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification


@receiver(post_save, sender=Notification)
def on_attendance_create(sender, instance: Notification, created, **kwargs):
    if not created and instance.is_read:
        notification = Notification.objects.get(id=instance.id)
        notification.delete()
        return

