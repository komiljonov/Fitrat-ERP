import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Monitoring , MonitoringAsos4, Monitoring5,StudentCatchingMonitoring,StudentCountMonitoring
from ...account.models import CustomUser


@receiver(post_save, sender=Monitoring)
def on_create(sender, instance: Monitoring, created, **kwargs):
    if created:
        instance.user.monitoring += instance.ball
        instance.user.save()


@receiver(post_save, sender=MonitoringAsos4)
def on_create(sender, instance: MonitoringAsos4, created, **kwargs):
    if created:
        instance.user.monitoring += instance.ball
        instance.user.save()


@receiver(post_save, sender=Monitoring5)
def on_create(sender, instance: Monitoring5, created, **kwargs):
    if created:
        instance.teacher.monitoring += instance.ball
        instance.teacher.save()


@receiver(post_save, sender=StudentCatchingMonitoring)
def on_create(sender, instance: StudentCatchingMonitoring, created, **kwargs):
    if created:
        instance.teacher.monitoring += instance.ball
        instance.teacher.save()


@receiver(post_save, sender=StudentCountMonitoring)
def on_create(sender, instance: StudentCountMonitoring, created, **kwargs):
    if created:
        instance.teacher.monitoring += instance.max_ball
        instance.teacher.save()
