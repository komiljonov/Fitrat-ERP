
import datetime
import logging
from cmath import isnan

from django.contrib.admin import action
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from icecream import ic

from .models import Results
from ..finances.compensation.models import MonitoringAsos4, Asos, ResultName, ResultSubjects
from ..finances.finance.models import Finance, Casher, Kind
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
                finance = Finance.objects.create(
                    casher=Casher.objects.filter(role="WEALTH").first(),
                    action="EXPENSE",
                    kind=Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first(),
                    amount=level.amount,
                    payment_method="Card",
                    stuff=instance.teacher,
                    comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                    "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!"
                )
                if finance.amount:
                    Notification.objects.create(
                        user=instance.teacher,
                        comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                        "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!",
                        come_from=instance,
                    )
                    logging.info(f"Sizga {level.amount} sum qo'shildi!")

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
                    finance = Finance.objects.create(
                        casher=Casher.objects.filter(role="WEALTH").first(),
                        action="EXPENSE",
                        kind=Kind.objects.filter(action="EXPENSE",name__icontains="Bonus").first(),
                        amount=level.amount,
                        payment_method="Card",
                        stuff=instance.teacher,
                        comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                        "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!"
                    )
                    if finance.amount:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                            "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!",
                            come_from=instance,
                        )
                        logging.info(
                            f"Sizga {level.amount} sum qo'shildi!"
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
                    finance = Finance.objects.create(
                        casher=Casher.objects.filter(role="WEALTH").first(),
                        action="EXPENSE",
                        kind=Kind.objects.filter(action="EXPENSE",name__icontains="Bonus").first(),
                        amount=level.amount,
                        payment_method="Card",
                        stuff=instance.teacher,
                        comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                        "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!"
                    )

                    if finance.amount:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                            "talabangiz natijasi"} uchun {level.amount} sum qo'shildi!",
                            come_from=instance,
                        )
                        logging.info(
                            f"Sizga {level.amount} sum qo'shildi!"
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

                DEGREE_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
                ic(instance.result_fk_name.name)

                point = ResultName.objects.filter(
                    name__icontains=instance.result_fk_name.name,
                    who=who,
                ).first()

                ic(point)

                if not point:
                    point = ResultName.objects.filter(
                        name__icontains=instance.result_fk_name.name,
                        who=who,
                    ).first()

                if not point:

                    name_exists = ResultName.objects.filter(
                        name__icontains=instance.result_fk_name.name
                    ).values_list('name', 'who', 'type', 'point_type')

                    point = ResultName.objects.filter(
                        name__icontains=instance.result_fk_name.name,
                    ).first()

                subject = None

                if point:
                    # Normalize band_score for comparison
                    band_score = str(instance.band_score).upper() if instance.band_score else None
                    ic(band_score)

                    if point.type == "Two":
                        # For type "Two", filter using range (from_point to to_point)
                        if point.point_type == "Percentage":
                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__lte=band_score,
                                to_point__gte=band_score,
                            ).first()
                        elif point.point_type == "Ball":
                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__lte=band_score,
                                to_point__gte=band_score,
                            ).first()
                        elif point.point_type == "Degree" and band_score in DEGREE_ORDER:
                            # Get all possible subjects first
                            possible_subjects = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                            )

                            # Filter in Python to check degree hierarchy
                            for subj in possible_subjects:
                                try:
                                    from_idx = DEGREE_ORDER.index(subj.from_point.upper())
                                    to_idx = DEGREE_ORDER.index(subj.to_point.upper())
                                    band_idx = DEGREE_ORDER.index(band_score)

                                    if from_idx <= band_idx <= to_idx:
                                        subject = subj
                                        break
                                except (ValueError, AttributeError):
                                    continue

                    elif point.type == "One":

                        if point.point_type == "Percentage":
                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__lte=band_score,
                            ).first()
                        elif point.point_type == "Ball":
                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__lte=band_score,
                            ).first()
                        elif point.point_type == "Degree" and band_score in DEGREE_ORDER:
                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__icontains=band_score,
                            ).first()

                    ic(subject)

                    if subject:
                        # Get the asos instance
                        asos = Asos.objects.filter(name__icontains="ASOS_4").first()

                        if asos:
                            ic("Max_Ball : ", subject.max_ball)
                            ball = MonitoringAsos4.objects.create(
                                creator=instance.teacher,
                                asos=asos,
                                user=instance.teacher,
                                subject=subject,
                                result=point,
                                ball=subject.max_ball
                            )
                            finance = Finance.objects.create(
                                casher=Casher.objects.filter(role="WEALTH").first(),
                                action="EXPENSE",
                                kind=Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first(),
                                amount=subject.amount,
                                payment_method="Card",
                                stuff=instance.teacher,
                                comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                                "talabangiz natijasi"} uchun {subject.amount} sum qo'shildi!"
                            )
                            if finance.amount:
                                Notification.objects.create(
                                    user=instance.teacher,
                                    comment=f"Sizga {"natijangiz" if instance.who == "Mine" else
                                    "talabangiz natijasi"} uchun {subject.amount} sum qo'shildi!",
                                    come_from=instance,
                                )
                                logging.info(
                                    f"Sizga {subject.amount} sum qo'shildi!"
                                )
                            if ball:
                                Notification.objects.create(
                                    user=instance.teacher,
                                    comment=f"Sizga {'natijangiz' if instance.who == who else 'talabangiz natijasi'} uchun {subject.max_ball} ball qo'shildi!",
                                    come_from=instance,
                                )