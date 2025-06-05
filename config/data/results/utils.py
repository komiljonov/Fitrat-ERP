from django.db.models import FloatField
from django.db.models.functions import Cast

from data.finances.compensation.models import Asos, ResultSubjects, ResultName
from data.finances.finance.models import Casher, Kind


def validate_olimpiada_requirements(instance):
    """Validate Olimpiada requirements without creating records"""
    # Check if teacher exists
    if not instance.teacher:
        raise ValueError("O'qituvchi ma'lumoti topilmadi!")

    # Check if ASOS_4 exists
    asos = Asos.objects.filter(name__icontains="ASOS_4").first()
    if not asos:
        raise ValueError("ASOS_4 topilmadi! Avval ASOS_4 yarating.")


    level = ResultSubjects.objects.filter(
        asos=asos,
        level=instance.level,
        degree=instance.degree,
    ).first()
    if not level:
        raise ValueError(
            f"Olimpiada uchun mos ResultSubjects topilmadi. Level: {instance.level}, Degree: {instance.degree}")

    if not hasattr(level, 'max_ball') or level.max_ball is None:
        raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Level ID: {level.id}")

    if not hasattr(level, 'amount') or level.amount is None:
        raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Level ID: {level.id}")

    # # Check if casher exists
    # casher = Casher.objects.filter(role="WEALTH").first()
    # if not casher:
    #     raise ValueError("WEALTH rolidagi kasher topilmadi!")


    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
    if not bonus_kind:
        raise ValueError("Bonus turi topilmadi!")


def validate_university_requirements(instance):
    """Validate University requirements without creating records"""
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

    # # Check if casher exists
    # casher = Casher.objects.filter(role="WEALTH").first()
    # if not casher:
    #     raise ValueError("WEALTH rolidagi kasher topilmadi!")

    # Check if bonus kind exists
    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
    if not bonus_kind:
        raise ValueError("Bonus turi topilmadi!")

    if instance.who == "Mine" or instance.who == "Student":
        entry = "Grant" if instance.university_entering_type == "Grant" else "Contract"

        level = ResultSubjects.objects.filter(
            asos__name__icontains="ASOS_4",
            entry_type=entry,
            university_type="Personal" if instance.university_type == "Unofficial" else "National",
        ).first()

        if not level:
            raise ValueError(
                f"University uchun mos ResultSubjects topilmadi. Entry: {entry}, University type: {instance.university_type}")

        # Check if max_ball and amount exist
        if not hasattr(level, 'max_ball') or level.max_ball is None:
            raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Level ID: {level.id}")

        if not hasattr(level, 'amount') or level.amount is None:
            raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Level ID: {level.id}")


def validate_certificate_requirements(instance):
    """Validate Certificate requirements without creating records"""
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
    # casher = Casher.objects.filter(role="WEALTH").first()
    # if not casher:
    #     raise ValueError("WEALTH rolidagi kasher topilmadi!")

    # Check if bonus kind exists
    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
    if not bonus_kind:
        raise ValueError("Bonus turi topilmadi!")

    who = "Mine" if instance.who == "Mine" else "Student"
    DEGREE_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

    point = ResultName.objects.filter(
        name__icontains=instance.result_fk_name.name,
        who=who,
    ).first()

    if not point:
        point = ResultName.objects.filter(
            name__icontains=instance.result_fk_name.name,
        ).first()

    if not point:
        raise ValueError(f"'{instance.result_fk_name.name}' nomli ResultName topilmadi!")

    # Validate band_score and find appropriate subject
    band_score = str(instance.band_score).upper() if instance.band_score else None
    subject = None

    if point.type == "Two":
        # For type "Two", filter using range (from_point to to_point)
        if point.point_type == "Percentage":
            try:
                band_score_float = float(band_score)

                subject = ResultSubjects.objects.annotate(
                    from_point_float=Cast("from_point", FloatField()),
                    to_point_float=Cast("to_point", FloatField()),
                ).filter(
                    asos__name__icontains="ASOS_4",
                    result=point,
                    result_type=who,
                    from_point_float__lte=band_score_float,
                    to_point_float__gte=band_score_float,
                ).first()
            except (ValueError, TypeError):
                raise ValueError(f"Band score '{band_score}' percentage formatida emas!")

        elif point.point_type == "Ball":
            try:
                band_score_float = float(band_score)

                subject = ResultSubjects.objects.annotate(
                    from_point_float=Cast("from_point", FloatField()),
                    to_point_float=Cast("to_point", FloatField()),
                ).filter(
                    asos__name__icontains="ASOS_4",
                    result=point,
                    result_type=who,
                    from_point_float__lte=band_score_float,
                    to_point_float__gte=band_score_float,
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

                subject = ResultSubjects.objects.annotate(
                    from_point_float=Cast("from_point", FloatField()),
                ).filter(
                    asos__name__icontains="ASOS_4",
                    result=point,
                    result_type=who,
                    from_point_float=band_score_float,
                ).first()
            except (ValueError, TypeError):
                raise ValueError(f"Band score '{band_score}' percentage formatida emas!")

        elif point.point_type == "Ball":
            try:
                band_score_float = float(band_score)

                subject = ResultSubjects.objects.annotate(
                    from_point_float=Cast("from_point", FloatField()),
                ).filter(
                    asos__name__icontains="ASOS_4",
                    result=point,
                    result_type=who,
                    from_point_float__lte=band_score_float,
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

    # if not subject:
    #     raise ValueError(
    #         f"Band score '{band_score}' uchun mos ResultSubjects topilmadi! Point: {point.name}, Type: {point.type}, Point type: {point.point_type}")

    # Check if max_ball and amount exist
    if not hasattr(subject, 'max_ball') or subject.max_ball is None:
        raise ValueError(f"ResultSubjects uchun max_ball qiymati topilmadi. Subject ID: {subject.id}")

    if not hasattr(subject, 'amount') or subject.amount is None:
        raise ValueError(f"ResultSubjects uchun amount qiymati topilmadi. Subject ID: {subject.id}")

