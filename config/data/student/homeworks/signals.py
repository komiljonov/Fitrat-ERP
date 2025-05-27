from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Homework,Homework_history
from ..mastering.models import Mastering
from ..quiz.models import Quiz
from ...notifications.models import Notification


@receiver(post_save, sender=Homework_history)
def on_create(sender, instance: Homework_history, created, **kwargs):
    if created:
        quiz = Quiz.objects.filter(homework=instance.homework).first()
        if instance.mark:
            mastering = Mastering.objects.create(
                student=instance.student,
                theme=instance.homework.theme,
                test=quiz,
                ball=instance.mark
            )
            if mastering:
                Notification.objects.create(
                    user=instance.student.user,
                    comment=f"Sizga {instance.homework.theme.title} mavzusi uchun {
                    instance.mark} ball quyildi va vazifa {"qayta topshirish" if instance.status == "Retake" else 
                    "bajarilmadi" if instance.status == "Failed" else "bajarildi"
                    } deb belgilandi ."
                )



@receiver(post_save, sender=Homework_history)
def on_update(sender, instance: Homework_history, created, **kwargs):

    if not created and instance.mark is not None:
        print("🔔 Signal triggered")
        quiz = Quiz.objects.filter(
            homework=instance.homework,
            theme=instance.homework.theme,
        ).first()

        mastering = Mastering.objects.filter(
            student=instance.student,
            theme=instance.homework.theme,
            test=quiz or None,
        ).first()

        if mastering:
            mastering.ball = instance.mark
            mastering.save(update_fields=['ball'])
            print(f"✅ Updated mastering ball to {mastering.ball}")
        else:
            print("❗ Mastering not found.")
