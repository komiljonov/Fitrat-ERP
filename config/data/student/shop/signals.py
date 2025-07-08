from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.autoreload import logger

from data.notifications.models import Notification
from data.student.shop.models import Coins, Purchase, Points
from data.student.student.models import Student
from data.finances.compensation.models import Page


@receiver(post_save, sender=Points)
def new_created_order(sender, instance: Points, created, **kwargs):
    if not created:
        return

    try:
        if hasattr(instance, 'student') and instance.student:
            user = Student.objects.filter(pk=instance.student.pk).first()
            if user:
                # Ensure instance.point is treated as Decimal
                user.points += Decimal(str(instance.point))
                user.save()
    except Exception as e:
        logger.error(f"Error in points signal handler: {str(e)}")


@receiver(post_save, sender=Coins)
def new_created_order(sender, instance: Coins, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user and instance.status == "Given":
            user.coins += instance.coin
            user.save()
        if user and instance.status == "Taken":
            user.coins -= instance.coin
            user.save()


@receiver(post_save, sender=Purchase)
def new_created_order(sender, instance: Purchase, created, **kwargs):
    student = instance.student

    if created:
        Coins.objects.create(
            student=student,
            coin=instance.product.coin,
            choice="Shopping",
            comment=f"Siz uchun {instance.product.name} buyurtma qilindi va tasdiqlanishi bilan sizga xabar beramiz .",
            status="Taken"
        )

    if not created and instance.status == "Completed":

        Notification.objects.create(
            user=student.user,
            comment=(
                f"Sizning kutish bosqichidagi {instance.product.name} nomli mahsulotamiz "
                f"sizga taqdim etish uchun tayyor.\n"
                f"Filial : {instance.product.filial}\n"
            ),
            choice="Shopping"
        )


    if not created and instance.status == "Cancelled":

        Coins.objects.create(
            student=student,
            coin=instance.product.coin,
            choice="Shopping",
            comment=f"Sizning kutish bosqichidagi {instance.product.name} buyurtmangiz bekir qilinganligi uchun coinlaringiz qaytarildi.",
            status="Given"
        )

        Notification.objects.create(
            user=student.user,
            comment=(
                f"Sizning kutish bosqichidagi {instance.product.name} nomli mahsulotamiz "
                f"bekor qilindi.\n"
                f"Filial : {instance.product.filial}\n"
            ),
            choice="Shopping"
        )

    if created:
        notifier_users = Page.objects.filter(is_readable=True)
        if notifier_users:
            for user in notifier_users:
                Notification.objects.create(
                    user=user.user,
                    comment=(
                        f"{instance.student.first_name} {instance.student.last_name} talaba  {instance.product.name} nomli mahsulot uchun "
                        f"coin orqali to'lov amalga oshirdi.\n"
                        f"Filial : {instance.product.filial}\n"
                    ),
                    choice="Shopping"
                )