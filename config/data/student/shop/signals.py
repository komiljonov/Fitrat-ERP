import json
from decimal import Decimal

from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.autoreload import logger

from data.notifications.models import Notification
from data.student.shop.models import Coins, Purchase, Points, Products
from data.student.student.models import Student
from data.finances.compensation.models import Page


@receiver(post_save, sender=Points)
def on_point_create(sender, instance: Points, created, **kwargs):
    if not created:
        return

    try:
        if hasattr(instance, "student") and instance.student:
            user = Student.objects.filter(pk=instance.student.pk).first()
            if user:
                # Ensure instance.point is treated as Decimal
                user.points += Decimal(str(instance.point))
                user.save()
    except Exception as e:
        logger.error(f"Error in points signal handler: {str(e)}")


@receiver(post_save, sender=Coins)
def on_coin_create(sender, instance: Coins, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user and instance.status == "Given":
            user.coins += instance.coin
            user.save()
        if user and instance.status == "Taken":
            user.coins -= instance.coin
            user.save()

@receiver(pre_save, sender=Purchase)
def set_filial_before_save(sender, instance: Purchase, **kwargs):
    if instance.student_id and not instance.filial_id:
        instance.filial = instance.student.filial

def _one_product(rel):
    if rel is None:
        return None
    return rel.first() if hasattr(rel, "all") else rel  # M2M vs FK

def _payload(instance: Purchase, product):
    return {
        "id": (str(product.id) if product else None),   # UUID -> str
        "name": (product.name if product else None),
        # "imageUrl": product.image.url if (product and product.image) else None,
        "coins": (int(product.coin) if product and product.coin is not None else None),
        "description": (product.comment if product else None),
        "status": instance.status,
        "date": timezone.localtime(instance.created_at).isoformat()
                if instance.created_at else None,       # datetime -> ISO
    }

@receiver(post_save, sender=Purchase)
def on_purchase_created(sender, instance: Purchase, created, **kwargs):
    student = instance.student
    product = _one_product(getattr(instance, "product", None))

    if created:
        # no instance.save() here anymore; handled in pre_save
        if product:
            Coins.objects.create(
                student=student,
                coin=product.coin,
                choice="Shopping",
                comment=f"Siz uchun {product.name} buyurtma qilindi va tasdiqlanishi bilan sizga xabar beramiz .",
                status="Taken",
            )
        return

    # Completed → decrement stock safely (no race)
    if instance.status == "Completed" and product:
        Products.objects.filter(pk=product.pk).update(quantity=F("quantity") - 1)
        data = _payload(instance, product)

        Notification.objects.create(
            user=student.user,
            comment=(
                f"Sizning kutish bosqichidagi {product.name} nomli mahsulotamiz "
                f"sizga taqdim etish uchun tayyor.\n"
                f"Filial : {product.filial}\n"
            ),
            come_from=json.dumps(data, cls=DjangoJSONEncoder),
            choice="Shopping",
        )

    # Cancelled → refund
    if instance.status == "Cancelled" and product:
        Coins.objects.create(
            student=student,
            coin=product.coin,
            choice="Shopping",
            comment=(f"Sizning kutish bosqichidagi {product.name} buyurtmangiz bekor "
                     f"qilinganligi uchun coinlaringiz qaytarildi."),
            status="Given",
        )
        data = _payload(instance, product)

        Notification.objects.create(
            user=student.user,
            comment=(
                f"Sizning kutish bosqichidagi {product.name} nomli mahsulotamiz "
                f"bekor qilindi.\n"
                f"Filial : {product.filial}\n"
            ),
            come_from=json.dumps(data, cls=DjangoJSONEncoder),
            choice="Shopping",
        )

    # if created:
    #     notifier_users = Page.objects.filter(is_readable=True)
    #     if notifier_users:
    #         for user in notifier_users:
    #             Notification.objects.create(
    #                 user=user.user,
    #                 comment=(
    #                     f"{instance.student.first_name} {instance.student.last_name} talaba  {instance.product.name} nomli mahsulot uchun "
    #                     f"coin orqali to'lov amalga oshirdi.\n"
    #                     f"Filial : {instance.product.filial}\n"
    #                 ),
    #                 come_from=instance.id,
    #                 choice="Shopping"
    #             )
