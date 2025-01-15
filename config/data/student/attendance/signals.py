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
