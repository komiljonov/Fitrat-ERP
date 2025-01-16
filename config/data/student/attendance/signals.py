from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Attendance
from ...notifications.models import Notification
from ...stages.models import NewOredersStages


@receiver(post_save, sender=Attendance)
def on_attendance_create(sender, instance: Attendance, created, **kwargs):
    # Exit early if the attendance does not have a lid
    if not instance.lid:
        return

    # Skip processing for students
    if instance.lid.is_student:
        return

    # Count all attendances for this Lid
    attendances_count = Attendance.objects.filter(lid=instance.lid).count()

    # First lesson attendance logic
    if attendances_count == 1:
        # Check attendance reason
        if instance.reason == "IS_PRESENT":
            stage_name = f"{attendances_count} darsga qatnashgan"
        else:
            stage_name = f"{attendances_count} darsga qatnashmagan"

        # Update the stage
        stage, created = NewOredersStages.objects.get_or_create(name=stage_name)
        instance.lid.ordered_stages = stage
        instance.lid.save()

    # Subsequent lessons logic
    elif attendances_count > 1 and instance.reason == "IS_PRESENT":
        # Handle balance deduction logic if required
        stage, created = NewOredersStages.objects.get_or_create(
            name=f"{attendances_count} darsga qatnashgan"
        )
        instance.lid.ordered_stages = stage
        instance.lid.save()

        Notification.objects.create(
            user=instance.lid.moderator,
            comment=f"Lead {instance.lid.first_name}  {instance.lid.phone_number} - {attendances_count} darsga to'lov qilmasdan qatnashgan !",
            come_from=instance.lid
        )

@receiver(post_save, sender=Attendance)
def on_attendance_money_back(sender, instance: Attendance, created, **kwargs):
    if created:
        if instance.reason == "IS_PRESENT" or instance.reason == "UNREASONED" and instance.lesson.group.price_type == "DAILY":
            instance.student.balance -= instance.lesson.group.price
            instance.student.save()
    if not created:
        if instance.reason == "REASONED":
            Notification.objects.create(
                user=instance.student.moderator and instance.student.call_operator,
                comment=f"{instance.student.first_name} {instance.student.phone_number}"
                        f" ning {instance.created_at} sanasidagi dars davomati sababli dars "
                        f"qoldirilganga o'zgartirildi, E'tiborli bo'ling bu dars uchun to'langan to'lov qaytarilishiga sabab bo'ldi ",
                come_from=instance.student,
            )



