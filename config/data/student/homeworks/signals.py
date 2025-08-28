from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Homework_history
from data.student.mastering.models import Mastering
from data.student.quiz.models import Quiz
from data.notifications.models import Notification


@receiver(post_save, sender=Homework_history)
def on_create(sender, instance: Homework_history, created, **kwargs):
    if created:
        instance.test_checked = True
        instance.save(update_fields=["test_checked"])
        quiz = Quiz.objects.filter(homework=instance.homework).first()
        if instance.mark:
            mastering = Mastering.objects.create(
                student=instance.student,
                theme=instance.homework.theme,
                test=quiz,
                choice="Homework",
                ball=instance.mark,
            )
            if mastering:
                Notification.objects.create(
                    user=instance.student.user,
                    comment=f"Sizga {instance.homework.theme.title} mavzusi uchun {
                    instance.mark} ball quyildi va vazifa {"qayta topshirish" if instance.status == "Retake" else 
                    "bajarilmadi" if instance.status == "Failed" else "bajarildi"
                    } deb belgilandi .",
                    choice="Homework",
                    come_from=instance.id,
                )


@receiver(post_save, sender=Homework_history)
def on_update(sender, instance: Homework_history, created, **kwargs):

    if not created and instance.mark is not None:
        print("🔔 Signal triggered")
        quiz = Quiz.objects.filter(
            homework=instance.homework, theme=instance.homework.theme
        ).first()

        mastering = Mastering.objects.filter(
            student=instance.student,
            theme=instance.homework.theme,
            test=quiz or None,
            choice="Homework",
        ).first()

        if mastering:
            mastering.ball = instance.mark
            mastering.save(update_fields=["ball"])
            print(f"✅ Updated mastering ball to {mastering.ball}")

            mastering.updater = instance.updater
            mastering.save(update_fields=["updater"])
            print(f"✅ Updated mastering updater to {mastering.ball}")

        else:
            print("❗ Mastering not found.")
