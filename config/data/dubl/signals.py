from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lid,Dubl
from ..student.student.models import Student


@receiver(post_save, sender=Lid)
def on_details_create(sender, instance: Lid, created, **kwargs):
    if not created or instance.phone_number:
        student = Student.objects.filter(phone_number=instance.phone_number).first()
        if student:
            instance.is_dubl = True
            instance.save()

            Dubl.objects.create(student=student,
                                lid=instance,
                                message=f"New Lid {instance.first_name} - {instance.phone_number} dubled with {student.first_name} - {student.phone_number} ",
                                )

# @receiver(post_save, sender=Dubl)
# def on_details_update(sender, instance: Dubl, created, **kwargs):
#     if not created or instance.on_merge:
#
#








