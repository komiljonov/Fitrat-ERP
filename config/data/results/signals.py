
import datetime
from cmath import isnan

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Results
from ..finances.compensation.models import MonitoringAsos4, Asos, ResultName, ResultSubjects
from ..notifications.models import Notification


@receiver(post_save, sender=Results)
def on_create(sender, instance: Results, created, **kwargs):
    # if not created and instance.status == "Accepted":
    #     asos = Asos.objects.filter(name__in = "Asos 4").first()
    #
    #     result_name = ResultName.objects.get(name=instance.name)
    #
    #     monitoring = MonitoringAsos4.objects.create(
    #         user=instance.teacher,
    #         asos=asos,
    #         result=instance,
    #
    #     )
    if created and instance.teacher and instance.teacher.filial.exists():
        instance.filial = instance.teacher.filial.first()
        instance.save()



@receiver(post_save, sender=Results)
def on_update(sender, instance: Results,created, **kwargs):
    if not created:
        if instance.status == "Accepted":
            if instance.results == "Olimpiada":
                if instance.who == "Mine":
                    level = ResultSubjects.objects.filter(
                        asos__name__icontains="ASOS_4",
                    ).first()
                    ball = MonitoringAsos4.objects.filter(
                        result__who="Mine",
                        user=instance.teacher,
                        subject=level,
                        result=None,
                        ball=level.max_ball
                    )
                    if ball:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                            "talabangiz natijasi"} uchun {level.max_ball} ball qo'shildi!",
                            come_from=instance,
                        )
                if instance.results == "Student":
                    level = ResultSubjects.objects.filter(
                        asos__name__icontains="ASOS_4",
                    ).first()
                    ball = MonitoringAsos4.objects.filter(
                        result__who="Student",
                        user=instance.teacher,
                        subject=level,
                        result=None,
                        ball=level.max_ball
                    )
                    if ball:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                            "talabangiz natijasi"} uchun {level.max_ball} ball qo'shildi!",
                            come_from=instance,
                        )


            if instance.results == "University":
                if instance.who == "Mine":
                    pass
                if instance.results == "Student":
                    pass