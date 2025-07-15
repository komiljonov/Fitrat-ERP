from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import MockExamResult, LevelExam, LevelExamResult
from ..student.groups.models import Group
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


@receiver(post_save, sender=LevelExam)
def on_create(sender, instance: LevelExam, created, **kwargs):
    if created:
        if instance.course and instance.subject and not instance.group:
            course = instance.course

            group = Group.objects.filter(course__id=course).all()

            students = StudentGroup.objects.filter(group__in=group).all()

            for student in students:
                res = LevelExamResult.objects.create(

                )
