from django.db.models.signals import post_save
from django.dispatch import receiver

from data.notifications.models import Notification
from data.student.shop.models import Coins, Purchase, Points
from data.student.student.models import Student


@receiver(post_save, sender=Points)
def new_created_order(sender, instance: Points, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user:
            user.points += instance.point
            user.save()


@receiver(post_save, sender=Coins)
def new_created_order(sender, instance: Coins, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user:
            user.coins += instance.coin
            user.save()


@receiver(post_save, sender=Purchase)
def new_created_order(sender, instance: Purchase, created, **kwargs):
    student = instance.student

    if created:
        # Subtract coins on creation
        student.coins -= instance.product.coin
        student.save()

    elif instance.status == "Completed":
        # Notify when marked as completed
        Notification.objects.create(
            user=student.user,
            comment=(
                f"Sizning kutish bosqichidagi {instance.product.name} nomli mahsulotamiz "
                f"sizga taqdim etish uchun tayyor.\n"
                f"Filial : {instance.product.filial.name}\n"
            )
        )


