import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Monitoring , MonitoringAsos4, Monitoring5,StudentCatchingMonitoring,StudentCountMonitoring
from ...account.models import CustomUser
from ...student.mastering.models import MasteringTeachers


@receiver(post_save, sender=Monitoring)
def on_create(sender, instance: Monitoring, created, **kwargs):
    if created:
        instance.user.monitoring += int(instance.ball)
        instance.user.save()


@receiver(post_save, sender=MonitoringAsos4)
def on_create(sender, instance: MonitoringAsos4, created, **kwargs):
    if created:
        instance.user.monitoring += int(instance.ball)
        instance.user.save()
        mastering = MasteringTeachers.objects.create(
            teacher=instance.user,
            reason=f"Sizga natijangiz uchun {instance.ball} ball qo'shildi!",
            ball=instance.ball
        )


@receiver(post_save, sender=Monitoring5)
def on_create(sender, instance: Monitoring5, created, **kwargs):
    if created:
        instance.teacher.monitoring += int(instance.ball)
        instance.teacher.save()


@receiver(post_save, sender=StudentCatchingMonitoring)
def on_create(sender, instance: StudentCatchingMonitoring, created, **kwargs):
    if created:
        instance.teacher.monitoring += int(instance.ball)
        instance.teacher.save()


@receiver(post_save, sender=StudentCountMonitoring)
def on_create(sender, instance: StudentCountMonitoring, created, **kwargs):
    if created:
        instance.teacher.monitoring += int(instance.max_ball)
        instance.teacher.save()
