import logging

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from icecream import ic

from .models import Results
from .utils import validate_olimpiada_requirements, validate_university_requirements, validate_certificate_requirements
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


@receiver(pre_save, sender=Results)
def validate_before_acceptance(sender, instance: Results, **kwargs):
    # Only process if status is being changed to "Accepted"
    if instance.status == "Accepted":
        try:
            # Check if this is an update (not creation) and status is actually changing
            if instance.pk:
                try:
                    original = Results.objects.get(pk=instance.pk)
                    if original.status == "Accepted":
                        return  # Status was already "Accepted", no need to process
                except Results.DoesNotExist:
                    pass  # New instance, continue processing

            # Validate all requirements before allowing the save
            if instance.results == "Olimpiada":
                validate_olimpiada_requirements(instance)

            elif instance.results == "University":
                validate_university_requirements(instance)

            elif instance.results == "Certificate":
                validate_certificate_requirements(instance)

            else:
                raise ValueError(f"Noma'lum results turi: {instance.results}")

        except Exception as e:
            # Log the error
            logging.error(f"Pre-save validation error: {str(e)}", exc_info=True)

            # Prevent the save by raising an exception
            raise ValueError(f"Ushbu natijani tasdiqlash uchun monitoring yaratilmagan! Xatolik: {str(e)}")


@receiver(post_save, sender=Results)
def on_update(sender, instance: Results, created, **kwargs):
    if not created:
        try:
            if instance.status == "Accepted":

                if instance.results == "Olimpiada":
                    who = "Mine" if instance.who == "Mine" else "Student"

                    # Check if ASOS_4 exists
                    asos = Asos.objects.filter(name__icontains="ASOS_4").first()
                    if not asos:
                        raise ValueError("ASOS_4 topilmadi! Avval ASOS_4 yarating.")

                    # Check if level exists
                    level = ResultSubjects.objects.filter(
                        asos=asos,
                        level=instance.level,
                        degree=instance.degree,
                    ).first()
                    if not level:
                        raise ValueError(
                            f"Olimpiada uchun mos ResultSubjects topilmadi. Level: {instance.level}, Degree: {instance.degree}")

                    # Check if teacher exists
                    if not instance.teacher:
                        raise ValueError("O'qituvchi ma'lumoti topilmadi!")

                    # Check if max_ball and amount exist
                    if not hasattr(level, 'max_ball') or level.max_ball is None:
                        raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Level ID: {level.id}")

                    if not hasattr(level, 'amount') or level.amount is None:
                        raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Level ID: {level.id}")

                    # Check if casher exists
                    casher = Casher.objects.filter(role="WEALTH").first()
                    if not casher:
                        raise ValueError("WEALTH rolidagi kasher topilmadi!")

                    # Check if bonus kind exists
                    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                    if not bonus_kind:
                        raise ValueError("Bonus turi topilmadi!")

                    # Create monitoring record
                    ball = MonitoringAsos4.objects.create(
                        creator=instance.teacher,
                        asos=asos,
                        user=instance.teacher,
                        subject=level,
                        result=None,
                        ball=level.max_ball
                    )

                    # Create finance record
                    finance = Finance.objects.create(
                        casher=casher,
                        action="EXPENSE",
                        kind=bonus_kind,
                        amount=level.amount,
                        stuff=instance.teacher,
                        comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.amount} sum qo'shildi!"
                    )

                    if finance.amount:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.amount} sum qo'shildi!",
                            come_from=instance,
                        )
                        logging.info(f"Sizga {level.amount} sum qo'shildi!")

                    if ball:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.max_ball} ball qo'shildi!",
                            come_from=instance,
                        )

                elif instance.results == "University":
                    if not instance.teacher:
                        raise ValueError("O'qituvchi ma'lumoti topilmadi!")

                    if not instance.university_entering_type:
                        raise ValueError("University entering type belgilanmagan!")

                    if not instance.university_type:
                        raise ValueError("University type belgilanmagan!")

                    # Check if ASOS_4 exists
                    asos = Asos.objects.filter(name__icontains="ASOS_4").first()
                    if not asos:
                        raise ValueError("ASOS_4 topilmadi! Avval ASOS_4 yarating.")

                    # Check if casher exists
                    casher = Casher.objects.filter(role="WEALTH").first()
                    if not casher:
                        raise ValueError("WEALTH rolidagi kasher topilmadi!")

                    # Check if bonus kind exists
                    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                    if not bonus_kind:
                        raise ValueError("Bonus turi topilmadi!")

                    if instance.who == "Mine" or instance.who == "Student":
                        entry = "Grant" if instance.university_entering_type == "Grant" else "Contract"
                        ic(entry)

                        level = ResultSubjects.objects.filter(
                            asos__name__icontains="ASOS_4",
                            entry_type=entry,
                            university_type="Personal" if instance.university_type == "Unofficial" else "National",
                        ).first()

                        if not level:
                            raise ValueError(
                                f"University uchun mos ResultSubjects topilmadi. Entry: {entry}, University type: {instance.university_type}")

                        ic(level)

                        # Check if max_ball and amount exist
                        if not hasattr(level, 'max_ball') or level.max_ball is None:
                            raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Level ID: {level.id}")

                        if not hasattr(level, 'amount') or level.amount is None:
                            raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Level ID: {level.id}")

                        ball = MonitoringAsos4.objects.create(
                            creator=instance.teacher,
                            user=instance.teacher,
                            subject=level,
                            result=None,
                            ball=level.max_ball
                        )

                        finance = Finance.objects.create(
                            casher=casher,
                            action="EXPENSE",
                            kind=bonus_kind,
                            amount=level.amount,
                            stuff=instance.teacher,
                            comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.amount} sum qo'shildi!"
                        )

                        if finance.amount:
                            Notification.objects.create(
                                user=instance.teacher,
                                comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.amount} sum qo'shildi!",
                                come_from=instance,
                            )
                            logging.info(f"Sizga {level.amount} sum qo'shildi!")

                        if ball:
                            Notification.objects.create(
                                user=instance.teacher,
                                comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {level.max_ball} ball qo'shildi!",
                                come_from=instance,
                            )

                elif instance.results == "Certificate":
                    if not instance.teacher:
                        raise ValueError("O'qituvchi ma'lumoti topilmadi!")

                    if not instance.result_fk_name:
                        raise ValueError("result_fk_name belgilanmagan!")

                    if not instance.band_score:
                        raise ValueError("band_score belgilanmagan!")

                    # Check if ASOS_4 exists
                    asos = Asos.objects.filter(name__icontains="ASOS_4").first()
                    if not asos:
                        raise ValueError("ASOS_4 topilmadi! Avval ASOS_4 yarating.")

                    # Check if casher exists
                    casher = Casher.objects.filter(role="WEALTH").first()
                    if not casher:
                        raise ValueError("WEALTH rolidagi kasher topilmadi!")

                    # Check if bonus kind exists
                    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                    if not bonus_kind:
                        raise ValueError("Bonus turi topilmadi!")

                    who = "Mine" if instance.who == "Mine" else "Student"
                    DEGREE_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]
                    ic(instance.result_fk_name.name)

                    point = ResultName.objects.filter(
                        name__icontains=instance.result_fk_name.name,
                        who=who,
                    ).first()

                    ic(point)

                    if not point:
                        name_exists = ResultName.objects.filter(
                            name__icontains=instance.result_fk_name.name
                        ).values_list('name', 'who', 'type', 'point_type')

                        point = ResultName.objects.filter(
                            name__icontains=instance.result_fk_name.name,
                        ).first()

                    if not point:
                        raise ValueError(f"'{instance.result_fk_name.name}' nomli ResultName topilmadi!")

                    subject = None

                    # Normalize band_score for comparison
                    band_score = str(instance.band_score).upper() if instance.band_score else None
                    ic(band_score)

                    if point.type == "Two":
                        # For type "Two", filter using range (from_point to to_point)
                        if point.point_type == "Percentage":
                            try:
                                band_score_float = float(band_score)
                                subject = ResultSubjects.objects.filter(
                                    asos__name__icontains="ASOS_4",
                                    result=point,
                                    result_type=who,
                                    from_point__lte=band_score_float,
                                    to_point__gte=band_score_float,
                                ).first()
                            except (ValueError, TypeError):
                                raise ValueError(f"Band score '{band_score}' percentage formatida emas!")

                        elif point.point_type == "Ball":
                            try:
                                band_score_float = float(band_score)
                                subject = ResultSubjects.objects.filter(
                                    asos__name__icontains="ASOS_4",
                                    result=point,
                                    result_type=who,
                                    from_point__lte=band_score_float,
                                    to_point__gte=band_score_float,
                                ).first()
                            except (ValueError, TypeError):
                                raise ValueError(f"Band score '{band_score}' ball formatida emas!")

                        elif point.point_type == "Degree":
                            if band_score not in DEGREE_ORDER:
                                raise ValueError(
                                    f"Band score '{band_score}' noto'g'ri degree formatida! Mumkin bo'lgan qiymatlar: {DEGREE_ORDER}")

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
                            try:
                                band_score_float = float(band_score)
                                subject = ResultSubjects.objects.filter(
                                    asos__name__icontains="ASOS_4",
                                    result=point,
                                    result_type=who,
                                    from_point=band_score_float,
                                ).first()
                            except (ValueError, TypeError):
                                raise ValueError(f"Band score '{band_score}' percentage formatida emas!")

                        elif point.point_type == "Ball":
                            try:
                                band_score_float = float(band_score)
                                subject = ResultSubjects.objects.filter(
                                    asos__name__icontains="ASOS_4",
                                    result=point,
                                    result_type=who,
                                    from_point=band_score_float,
                                ).first()
                            except (ValueError, TypeError):
                                raise ValueError(f"Band score '{band_score}' ball formatida emas!")

                        elif point.point_type == "Degree" and band_score:
                            if band_score not in DEGREE_ORDER:
                                raise ValueError(
                                    f"Band score '{band_score}' noto'g'ri degree formatida! Mumkin bo'lgan qiymatlar: {DEGREE_ORDER}")

                            subject = ResultSubjects.objects.filter(
                                asos__name__icontains="ASOS_4",
                                result=point,
                                result_type=who,
                                from_point__icontains=band_score,
                            ).first()

                    ic(subject)

                    if not subject:
                        raise ValueError(
                            f"Band score '{band_score}' uchun mos ResultSubjects topilmadi! Point: {point.name}, Type: {point.type}, Point type: {point.point_type}")

                    # Check if max_ball and amount exist
                    if not hasattr(subject, 'max_ball') or subject.max_ball is None:
                        raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Subject ID: {subject.id}")

                    if not hasattr(subject, 'amount') or subject.amount is None:
                        raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Subject ID: {subject.id}")

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
                        casher=casher,
                        action="EXPENSE",
                        kind=bonus_kind,
                        amount=subject.amount,
                        stuff=instance.teacher,
                        comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {subject.amount} sum qo'shildi!"
                    )

                    if finance.amount:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {'natijangiz' if instance.who == 'Mine' else 'talabangiz natijasi'} uchun {subject.amount} sum qo'shildi!",
                            come_from=instance,
                        )
                        logging.info(f"Sizga {subject.amount} sum qo'shildi!")

                    if ball:
                        Notification.objects.create(
                            user=instance.teacher,
                            comment=f"Sizga {'natijangiz' if instance.who == who else 'talabangiz natijasi'} uchun {subject.max_ball} ball qo'shildi!",
                            come_from=instance,
                        )

                else:
                    raise ValueError(f"Noma'lum results turi: {instance.results}")

        except Exception as e:

            logging.error(f"Signal handler error: {str(e)}", exc_info=True)

            Results.objects.filter(pk=instance.pk).update(status="Pending")


@receiver(post_save, sender=Results)
def send_notf(sender, instance : Results, created, **kwargs):
    if not created:
        if instance.status == "Rejected":
            Notification.objects.create(
                user=instance.teacher,
                comment=f"Sizning {instance.band_score} ballik natijangiz bekor qilindi!",
                come_from=instance,
            )