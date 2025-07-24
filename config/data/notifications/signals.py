from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Notification, UserRFToken
from .send_notifications import send_push_notification


@receiver(post_save, sender=Notification)
def on_attendance_create(sender, instance: Notification, created, **kwargs):
    """Delete notification if it is read."""
    if not created and instance.is_read:
        instance.delete()  # Directly delete the instance
        return


@receiver(post_save, sender=Notification)
def send_notification_on_create(sender, instance : Notification, created, **kwargs):
    if not created:
        return

    user = instance.user
    fcm_token = UserRFToken.objects.filter(user=user).first()
    if not fcm_token:
        print("❌ No FCM token found for user.")
        return

    send_push_notification(
        title="Fitrat",
        body=instance.comment,
        token=fcm_token.token,
    )
