
import datetime
from cmath import isnan

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Results
from ..finances.compensation.models import MonitoringAsos4


@receiver(post_save, sender=Results)
def on_create(sender, instance: Results, created, **kwargs):
    if not created and instance.status == "Accepted":
        monitoring = MonitoringAsos4.objects.create(
            user=instance.teacher,
            
        )

