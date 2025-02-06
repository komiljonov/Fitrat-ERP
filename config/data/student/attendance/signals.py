from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Attendance
from ..groups.models import Group
from ...notifications.models import Notification
from ...stages.models import NewOredersStages


@receiver(post_save, sender=Attendance)
def on_attendance_create(sender, instance: Attendance, created, **kwargs):

    if instance.lid:

        attendances_count = Attendance.objects.filter(lid=instance.lid).count()

        if attendances_count == 1:
            if instance.reason == "IS_PRESENT":
                instance.lid.is_student = True
                instance.lid.save()
            else:
                stage_name = f"{attendances_count} darsga qatnashmagan"
                Notification.objects.create(
                    user=instance.lid.call_operator,
                    comment=f"Lead {instance.lid.first_name} {instance.lid.phone_number} - {stage_name} !",
                    come_from=instance.lid,
                )
                instance.lid.ordered_stages = "BIRINCHI_DARSGA_KELMAGAN"
                instance.lid.save()

        elif attendances_count > 1 and instance.reason == "UNREASONED":

            Notification.objects.create(
                user=instance.lid.moderator,
                comment=f"Lead {instance.lid.first_name} {instance.lid.phone_number} - {attendances_count} darsga qatnashmagan!",
                come_from=instance.lid,
            )
    if instance.student:
        attendances_count = Attendance.objects.filter(student=instance.student).count()
        if attendances_count > 1 and instance.reason == "IS_PRESENT":
            if instance.student.balance_status =="INACTIVE":
                Notification.objects.create(
                    user=instance.student.sales_manager,
                    comment=f"Talaba {instance.student.first_name} {instance.student.phone} - "
                            f"{attendances_count} darsga qatnashdi va balansi statusi inactive, To'lov haqida ogohlantiring!",
                    come_from=instance.lid,
                )
        if attendances_count > 1 and instance.reason == "UNREASONED":

            Notification.objects.create(
                user=instance.student.sales_manager,
                comment=f"Talaba {instance.student.first_name} {instance.student.phone} - {attendances_count} darsga qatnashmagan!",
                come_from=instance.student,
            )


@receiver(post_save, sender=Attendance)
def on_attendance_money_back(sender, instance: Attendance, created, **kwargs):
    if created:
        if (
                instance.reason in ["IS_PRESENT", "UNREASONED"]
                and instance.group
        ):
            if instance.group.price_type == "DAILY":
                if instance.student:
                    instance.student.balance -= instance.group.price
                    instance.student.save()
                else:
                    print("Attendance does not have a related student.")

    if not created:
        if instance.reason == "REASONED":
            if instance.student:
                Notification.objects.create(
                    user=instance.student.moderator or instance.student.call_operator,
                    comment=f"{instance.student.first_name} {instance.student.phone} "
                            f"ning {instance.created_at} sanasidagi dars davomati sababli dars "
                            f"qoldirilganga o'zgartirildi. E'tiborli bo'ling, bu dars uchun to'langan to'lov qaytarilishiga sabab bo'ldi.",
                    come_from=instance.student,
                )
            else:
                print("Attendance does not have a related student.")
