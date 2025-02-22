from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import MasteringTeachers
from ..attendance.models import Attendance
from ...account.models import CustomUser
from ...finances.compensation.models import Bonus
from ...notifications.models import Notification


@receiver(post_save, sender=MasteringTeachers)
def on_create(sender, instance: MasteringTeachers, created, **kwargs):
    if created:
        user = CustomUser.objects.filter(id=instance.teacher.id, role="TEACHER").first()
        if user:
            user.ball += instance.ball
            user.save()
            Notification.objects.create(
                user=user,
                comment=f"Sizning darajangiz {instance.ball} ball oshirildi ! ",
                come_from=instance
            )

#------------- Monitoring edits -----------#

@receiver(post_save, sender=Attendance)
def bonus_call_operator(sender, instance: Attendance, created, **kwargs):
    if created:
        attendances_count = Attendance.objects.filter(student=instance.student).count()
        if attendances_count == 1:
            bonus = Bonus.objects.filter(user=instance.student.call_operator, name="Markazga kelgan oq’uvchi uchun bonus").first()
            if bonus:
                instance.student.call_operator += bonus
                instance.student.save()

