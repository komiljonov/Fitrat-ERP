from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template.context_processors import request

from .models import Finance

@receiver(post_save, sender=Finance)
def on_create(sender, instance: Finance, created, **kwargs):

    if instance and instance.student:
        if instance.action == "INCOME":
            pass

