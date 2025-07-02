
from decimal import Decimal
from itertools import count

from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver
from icecream import ic

from .models import MockExam, MockExamResult
from ..student.mastering.models import Mastering
from ..student.studentgroup.models import StudentGroup


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


