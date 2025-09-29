from datetime import timedelta

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Group, SecondaryGroup, Day, GroupSaleStudent
from data.student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from data.student.subject.models import Theme
from data.account.models import CustomUser
# from data.department.marketing_channel.models import Group_Type
from data.finances.finance.models import SaleStudent, Sale
from data.notifications.models import Notification


# @receiver(pre_save, sender=Group)
# def set_price_type_on_create(sender, instance: Group, **kwargs):
#     if instance.pk is None and not instance.price_type:
#         group_type = Group_Type.objects.first()
#         if group_type and group_type.price_type:
#             instance.price_type = group_type.price_type


@receiver(post_save, sender=Group)
def on_create(sender, instance: Group, created, **kwargs):
    if created and instance.is_secondary is True:
        secondary = SecondaryGroup.objects.create(
            name=f"{instance.name} ning yordamchi guruhi",
            teacher=instance.secondary_teacher,
            status="ACTIVE",
            group=instance,
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
                    lid=i.lid if i.lid else None,
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


# @receiver(post_save, sender=Group)
# def on_payment_method(sender, instance: Group, created: bool, **kwargs):
#     if created:
#         group_count = Group.objects.all().count()
#         if group_count == 1:
#             Group_Type.objects.create(price_type=instance.price_type)


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


UZBEK_WEEKDAYS = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]


@receiver(post_save, sender=Group)
def group_finish_date(sender, instance: Group, created: bool, **kwargs):
    if created and instance.finish_date is None:
        themes = Theme.objects.filter(
            course=instance.course, level=instance.level, is_archived=False
        )
        total_lessons = themes.count()

        scheduled_days = (
            instance.scheduled_day_type.all()
        )  # Assume this gives Uzbek day names
        scheduled_day_numbers = [
            UZBEK_WEEKDAYS.index(day.name)
            for day in scheduled_days
            if day.name in UZBEK_WEEKDAYS
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

        instance.finish_date = finish_date - timedelta(
            days=1
        )  # subtract last extra day

        instance.save(update_fields=["finish_date"])


@receiver(post_save, sender=GroupSaleStudent)
def add_sales_student(sender, instance: GroupSaleStudent, created: bool, **kwargs):
    if created:

        amount = instance.group.price - instance.amount
        creator = CustomUser.objects.filter(role="DIRECTOR").first()
        sale = Sale.objects.create(
            creator=creator,
            name="Sale",
            status="ACTIVE",
            amount=amount,
        )
        sale_student = SaleStudent.objects.create(
            student=instance.student if instance.student else None,
            sale=sale,
            lid=instance.lid if instance.lid else None,
            creator=creator,
        )
