from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import Student
from ...notifications.models import Notification


@receiver(post_save, sender=Student)
def on_create(sender, instance: Student, created, **kwargs):
    if not created :
        if instance.balance <= 50000 :
            Notification.objects.create(
                user=instance.call_operator,
                comment=f"{instance.first_name} {instance.last_name} ning balance miqdori {instance.balance} sum,"
                        f" to'lov amalga oshirishi haqida eslating !",
                come_from=instance,
            )

        if instance.balance < 50000 :
            if instance.balance_status == "ACTIVE":
                instance.balance_status = "INACTIVE"
                instance.save()

            Notification.objects.create(
                user=instance.call_operator,
                comment=f"{instance.first_name} {instance.last_name} ning balance miqdori {instance.balance} sum,"
                        f" to'lov amalga oshirishi haqida eslating !",
                come_from=instance,
            )











