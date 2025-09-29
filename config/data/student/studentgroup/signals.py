from django.dispatch import receiver
from django.db.models.signals import post_save

from data.student.studentgroup.models import StudentGroupPrice


@receiver(post_save, sender=StudentGroupPrice)
def on_new_student_group_price(sender, instance: StudentGroupPrice, created, **kwargs):

    if not created:
        return

    instance.student_group.price = instance.amount
    instance.student_group.price_comment = instance.comment
    instance.student_group.save()
