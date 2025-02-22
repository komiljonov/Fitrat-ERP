from cmath import isnan

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import FirstLLesson, ExtraLessonGroup, ExtraLesson
from ..studentgroup.models import StudentGroup
from ...notifications.models import Notification

@receiver(post_save, sender=FirstLLesson)
def on_create(sender, instance: FirstLLesson, created, **kwargs):
    if created:
        student = StudentGroup.objects.get_or_create(
            group=instance.group,
            student=None,
            lid=instance.lid if instance.lid else None,
        )
        # notif = Notification.objects.create(
        #     user=instance.creator,
        #     comment="First Lesson",
        #     come_from=instance,
        # )
        # if notif:
        #     print(notif)
        # else:
        #     return "Notification not created couse creator is not here ???"

    if created and instance.lid.lid_stage_type == "ORDERED_LID":
        instance.lid.ordered_stages = "BIRINCHI_DARS_BELGILANGAN"
        instance.lid.save()


@receiver(post_save, sender=ExtraLessonGroup)
def on_create(sender, instance: ExtraLessonGroup, created, **kwargs):
    if created:
        students = StudentGroup.objects.filter(
            group=instance.group,
        ).all()
        if students:
            # for student in students:
            #     Notification.objects.create(
            #         user=student,
            #         comment = f"Siz uchun {instance.date} da {instance.group.name} "
            #                   f"guruhi bilan qo'shimcha dars belgilandi !",
            #         come_from=instance,
            #     )
            Notification.objects.create(
                user=instance.group.teacher,
                comment = f"Siz uchun {instance.date} da {instance.group.name} guruhi uchun qo'shimcha dars belgilandi ! ",
                come_from=instance,
            )

@receiver(post_save, sender=ExtraLesson)
def on_create(sender, instance: ExtraLesson, created, **kwargs):
    if created:
        # Notification.objects.create(
        #     user=instance.student,
        #     comment=f"Siz uchun {instance.date} sanasida qo'shimcha dars belgilandi !",
        #     come_from=instance,
        # )
        Notification.objects.create(
            user=instance.teacher,
            comment=f"Siz uchun {instance.date} sanasida qo'shimcha dars belgilandi !",
            come_from=instance,
        )




