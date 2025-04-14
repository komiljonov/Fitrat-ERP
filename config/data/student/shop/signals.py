from django.db.models.signals import post_save
from django.dispatch import receiver

from data.student.shop.models import Coins, Purchase
from data.student.student.models import Student


@receiver(post_save, sender=Coins)
def new_created_order(sender, instance: Coins, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user:
            user.coins += instance.coin
            user.save()


@receiver(post_save, sender=Purchase)
def new_created_order(sender, instance: Purchase, created, **kwargs):
    if created:
        user = Student.objects.filter(pk=instance.student.pk).first()
        if user:
            user.coins -= instance.product.coin
            user.save()


