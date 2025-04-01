from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Group, SecondaryGroup
from ...notifications.models import Notification


@receiver(post_save, sender=Group)
def on_create(sender, instance: Group, created, **kwargs):
    if created and instance.is_secondary == True:
        secondary = SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            group=instance
        )
        secondary.scheduled_day_type.set(instance.scheduled_day_type.all())
        secondary.filial.set(instance.teacher.filial.all())


        Notification.objects.create(
            user=instance.secondary_teacher,
            comment=f"{instance.name} guruhining yordamchi guruhi yaratildi !",
            come_from=instance,
        )

    if not created and instance.is_secondary == True:
        SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            group=instance)

        Notification.objects.create(
            user=instance.secondary_teacher,
            comment=f"{instance.name} guruhining yordamchi guruhi yaratildi !",
            come_from=instance,
        )



