from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Group, SecondaryGroup, Day
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...department.marketing_channel.models import Group_Type
from ...notifications.models import Notification


@receiver(post_save, sender=Group)
def on_create(sender, instance: Group, created, **kwargs):
    if created and instance.is_secondary is True:
        secondary = SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            status="ACTIVE",
            group=instance
        )

        first_day = instance.scheduled_day_type.first()
        if first_day:
            if first_day.name == "Dushanba":
                week_days = ["Seshanba", "Payshanba", "Shanba"]

            else:
                week_days = ["Dushanba", "Chorshanba", "Juma"]

            day_objs = Day.objects.filter(name__in=week_days)

            secondary.scheduled_day_type.set(day_objs)
        else:
            secondary.scheduled_day_type.clear()

        secondary.filial = instance.teacher.filial.first()
        secondary.save()

        if StudentGroup.objects.filter(group=instance).exists():
            student = StudentGroup.objects.filter(group=instance)
            for i in student:
                SecondaryStudentGroup.objects.create(
                    group=secondary,
                    student=i.student if i.student else None,
                    lid=i.lid if i.lid else None
                )

        Notification.objects.create(
            user=instance.secondary_teacher,
            comment=f"{instance.name} guruhining yordamchi guruhi yaratildi!",
            come_from=instance,
        )

    if not created and instance.is_secondary == True:
        secondary_group = SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            group=instance)
        if StudentGroup.objects.filter(group=instance).exists():
            student = StudentGroup.objects.filter(group=instance)
            for i in student:
                SecondaryStudentGroup.objects.create(
                    group=secondary_group,
                    student=i.student if i.student else None,
                    lid=i.lid if i.lid else None
                )

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
