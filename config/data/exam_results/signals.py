from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MockExamResult
from ..student.mastering.models import Mastering


@receiver(post_save, sender=MockExamResult)
def on_create(sender, instance: MockExamResult, created, **kwargs):
    if created:
        mastering = Mastering.objects.create(
            theme=None,
            student=instance.student,
            lid=None,
            choice="Mock",
            mock=instance.mock,
            test=None,
        )
