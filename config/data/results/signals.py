
import datetime
from cmath import isnan

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from icecream import ic

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
                who = "Mine" if instance.who == "Mine" else "Student"
                ic(who)
                ic(instance.degree)
                ic(instance.level)
                asos = Asos.objects.filter(
                    name__icontains="ASOS_4",
                ).first()
                ic(asos)

                level = ResultSubjects.objects.filter(
                    asos=asos,
                    level=instance.level,
                    degree=instance.degree,
                ).first()
                ic(level)

                ball = MonitoringAsos4.objects.create(
                    creator=instance.teacher,
                    asos=asos,
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
                    entry = "Grant" if instance.university_entering_type == "Grant" else "Contract"
                    ic(entry)
                    level = ResultSubjects.objects.filter(
                        asos__name__icontains="ASOS_4",
                        entry_type=entry,
                        university_type="Personal" if instance.university_type == "Unofficial" else "National",
                    ).first()

                    ic(level)

                    ball = MonitoringAsos4.objects.create(
                        creator=instance.teacher,
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

                if instance.who == "Student":
                    entry = "Grant" if instance.university_entering_type == "Grant" else "Contract"
                    ic(entry)
                    ic(instance.university_type)
                    level = ResultSubjects.objects.filter(
                        asos__name__icontains="ASOS_4",
                        entry_type=entry,
                        university_type="Personal" if instance.university_type == "Unofficial" else "National",
                    ).first()

                    ic(level)

                    ball = MonitoringAsos4.objects.create(
                        creator=instance.teacher,
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


            if instance.results == "Certificate":
                who = "Mine" if instance.who == "Mine" else "Student"

                ic(instance.result_fk_name.name)
                ic(who)
                point = ResultName.objects.filter(
                    name__icontains=instance.result_fk_name.name,
                    who=who,
                ).first()
                ic(point)

                subject = None

                # Check the type and point_type to determine filtering logic
                if point.type == "Two":
                    # For type "Two", filter using from_point and to_point range
                    if point.point_type == "Percentage":
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            from_point__lte=str(instance.band_score),  # Convert to string for comparison
                            to_point__gte=str(instance.band_score),
                        ).first()
                    elif point.point_type == "Ball":
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            from_point__lte=str(instance.band_score),
                            to_point__gte=str(instance.band_score),
                        ).first()
                    elif point.point_type == "Degree":
                        # For degree, you might want to match exact degree value
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            degree=str(instance.band_score),  # Assuming band_score contains degree value
                        ).first()

                elif point.type == "One":
                    # For type "One", use the original logic with from_point comparison
                    if point.point_type == "Percentage":
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            from_point__lte=str(instance.band_score),
                        ).first()
                    elif point.point_type == "Ball":
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            from_point__lte=str(instance.band_score),
                        ).first()
                    elif point.point_type == "Degree":
                        subject = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            result=point,
                            result_type=who,
                            degree=str(instance.band_score),
                        ).first()

                ic(subject)

                if subject:
                    # Get the asos instance
                    asos = Asos.objects.filter(name__icontains="ASOS_4").first()

                    if asos:
                        ic("Max_Ball : ",subject.max_ball)
                        ball = MonitoringAsos4.objects.create(
                            creator=instance.teacher,  # Added creator field
                            asos=asos,  # Added asos field (assuming it's required)
                            user=instance.teacher,
                            subject=subject,
                            result=point,
                            ball=subject.max_ball
                        )
                        if ball:
                            Notification.objects.create(
                                user=instance.teacher,
                                comment=f"Sizga {"natijangiz" if instance.who == who else "talabangiz natijasi"} uchun {subject.max_ball} ball qo'shildi!",
                                come_from=instance,
                            )