from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Homework,Homework_history
from ..mastering.models import Mastering


# @receiver(post_save, sender=Homework_history)
# def on_create(sender, instance: Homework_history, created, **kwargs):
#     if created:
#         if instance.mark:
#             student =
#             mastering = Mastering.objects.create(
#                 student=instance.homework.
#             )