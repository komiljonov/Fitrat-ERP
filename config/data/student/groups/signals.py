from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from faker.providers.ssn.uk_UA import calculate_day_count

from .lesson_date_calculator import calculate_lessons
from .models import Group, SecondaryGroup, Day, GroupSaleStudent
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ..subject.models import Theme
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

    # if not created and instance.is_secondary == True:
    #     secondary_group = SecondaryGroup.objects.create(
    #         name=f"{instance.name} ning yordamchi guruhi",
    #         teacher=instance.secondary_teacher,
    #         group=instance)
    #     if StudentGroup.objects.filter(group=instance).exists():
    #         student = StudentGroup.objects.filter(group=instance)
    #         for i in student:
    #             SecondaryStudentGroup.objects.create(
    #                 group=secondary_group,
    #                 student=i.student if i.student else None,
    #                 lid=i.lid if i.lid else None
    #             )
    #
    #     Notification.objects.create(
    #         user=instance.secondary_teacher,
    #         comment=f"{instance.name} guruhining yordamchi guruhi yaratildi !",
    #         come_from=instance,
    #     )


@receiver(post_save, sender=Group)
def on_payment_method(sender, instance: Group, created: bool, **kwargs):
    if created:
        group_count = Group.objects.all().count()
        if group_count == 1:
            Group_Type.objects.create(
                price_type=instance.price_type
            )


@receiver(post_save, sender=Group)
def on_group_price_change(sender, instance: Group, created: bool, **kwargs):
    if created:
        return

    try:
        old_instance = Group.objects.get(pk=instance.pk)
    except Group.DoesNotExist:
        return

    if old_instance.price != instance.price:
        price = instance.price

        group_students = GroupSaleStudent.objects.filter(group=instance)

        for student in group_students:
            student.amount = price
            student.save()


UZBEK_WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]

@receiver(post_save, sender=Group)
def group_finish_date(sender, instance: Group, created: bool, **kwargs):
    if created and instance.finish_date is None:
        themes = Theme.objects.filter(course=instance.course, level=instance.level)
        total_lessons = themes.count()

        scheduled_days = instance.scheduled_day_type.all()  # Assume this gives Uzbek day names
        scheduled_day_numbers = [
            UZBEK_WEEKDAYS.index(day.name) for day in scheduled_days if day.name in UZBEK_WEEKDAYS
        ]

        if not scheduled_day_numbers:
            return  # Can't calculate finish date without schedule

        start_date = instance.start_date
        finish_date = start_date
        lessons_scheduled = 0

        while lessons_scheduled < total_lessons:
            if finish_date.weekday() in scheduled_day_numbers:
                lessons_scheduled += 1
            finish_date += timedelta(days=1)

        instance.finish_date = finish_date - timedelta(days=1)  # subtract last extra day
        instance.save(update_fields=["finish_date"])
