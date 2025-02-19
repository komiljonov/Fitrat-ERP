import icecream
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification
from ..notifications import send_notifications as fcm

@receiver(post_save, sender=Notification)
def on_attendance_create(sender, instance: Notification, created, **kwargs):
    """Delete notification if it is read."""
    if not created and instance.is_read:
        instance.delete()  # Directly delete the instance
        return

@receiver(post_save, sender=Notification)
def on_attendance_update(sender, instance: Notification, created, **kwargs):
    """Send push notification when a new notification is created."""
    if created and instance.user.role==["TEACHER","ASSISTANT"]:
        icecream.ic(instance.user.pk)
        fcm.send_push_notification(
            title="Notification !",
            body=instance.comment,
            topic=instance.user.pk
        )
        print(f"Notification sent to user_{instance.user.pk}")