from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import MasteringTeachers
from ...account.models import CustomUser
from ...notifications.models import Notification


@receiver(post_save, sender=MasteringTeachers)
def on_create(sender, instance: MasteringTeachers, created, **kwargs):
    if created:
        user = CustomUser.objects.filter(id=instance.teacher.id, role="TEACHER").first()
        if user:
            user.ball += instance.ball
            user.save()
            Notification.objects.create(
                user=user,
                comment=f"Sizning darajangiz {instance.ball} ball oshirildi ! ",
                come_from=instance
            )


