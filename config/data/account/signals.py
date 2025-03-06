from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def on_create(sender, instance: CustomUser, created, **kwargs):
    if created :
        instance.full_name = instance.first_name + " " + instance.last_name
        instance.save()






