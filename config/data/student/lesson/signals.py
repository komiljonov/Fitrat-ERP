from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import  FirstLLesson
from ..studentgroup.models import StudentGroup
from ...notifications.models import Notification

@receiver(post_save, sender=FirstLLesson)
def on_create(sender, instance: FirstLLesson, created, **kwargs):
    if created:
        student = StudentGroup.objects.get_or_create(
            group=instance.group,
            student=None,
            lid=instance.lid if instance.lid else None,
        )
        notif = Notification.objects.create(
            user=instance.creator,
            comment="First Lesson",
            come_from=instance,
        )
        if notif:
            print(notif)
        else:
            return "Notification not created couse creator is not here ???"
