from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Group_Type
from ...account.models import CustomUser
from ...notifications.models import Notification
from ...student.groups.models import Group


@receiver(post_save, sender=Group_Type)
def on_create(sender, instance: Group_Type, created, **kwargs):
    if not created :
        for group in Group.objects.all():
            group.price_type = instance.price_type
            group.save()
    Notification.objects.create(
        user=[user for user in CustomUser.objects.filter(
            role__in=["DIRECTOR", "ACCOUNTING"])],
        comment=f"Guruhlarning to'lov uslubi {instance.price_type} ga o'zgartirildi !",
        come_from=Group.objects.filter().first(),
    )