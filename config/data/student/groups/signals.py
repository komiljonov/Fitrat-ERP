from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Group, SecondaryGroup
from ...department.marketing_channel.models import Group_Type
from ...notifications.models import Notification


@receiver(post_save, sender=Group)
def on_create(sender, instance: Group, created, **kwargs):
    if created and instance.is_secondary is True:
        secondary = SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            group=instance
        )

        secondary.filial = instance.teacher.filial.first()
        secondary.save()

        Notification.objects.create(
            user=instance.secondary_teacher,
            comment=f"{instance.name} guruhining yordamchi guruhi yaratildi!",
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


@receiver(post_save, sender=Group)
def on_payment_method(sender, instance: Group, created: bool, **kwargs):
    if created:
        group_count = Group.objects.all().count()
        if group_count == 1:
             Group_Type.objects.create(
                 price_type=instance.price_type
             )
