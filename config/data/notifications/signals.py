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
    if created:
        fcm.send_push(
            title="Notification !",
            msg=instance.comment,
            topics=f"user_{instance.user.pk}",  # Ensure the topic is passed as a string
        )
        print(f"Notification sent to user_{instance.user.pk}")