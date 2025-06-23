import calendar
from datetime import date, datetime

import pytz
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import make_aware, is_aware
from icecream import ic

from data.account.models import CustomUser
from data.finances.finance.models import Finance, Kind
from data.finances.timetracker.models import UserTimeLine, Stuff_Attendance
from data.student.groups.models import Group
from data.student.studentgroup.models import StudentGroup

TASHKENT_TZ = pytz.timezone("Asia/Tashkent")

UZBEK_WEEKDAYS = {
    'Dushanba': 0,
    'Seshanba': 1,
    'Chorshanba': 2,
    'Payshanba': 3,
    'Juma': 4,
    'Shanba': 5,
    'Yakshanba': 6
}


def localize(dt):
    return make_aware(dt, timezone=TASHKENT_TZ) if not is_aware(dt) else dt.astimezone(TASHKENT_TZ)


def get_monthly_per_minute_salary(user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    if not user or not user.salary:
        return {"total_minutes": 0, "per_minute_salary": 0}

    today = date.today()
    _, days_in_month = calendar.monthrange(today.year, today.month)
    total_minutes = 0

    if user.role in {"TEACHER", "ASSISTANT"}:
        student_groups = StudentGroup.objects.filter(
            Q(group__teacher=user) | Q(group__secondary_teacher=user)
        ).select_related('group')

        group_ids = [sg.group.id for sg in student_groups]
        groups = Group.objects.filter(id__in=group_ids).prefetch_related('scheduled_day_type')

        for group in groups:
            if not group.started_at or not group.ended_at:
                continue

            session_start = datetime.combine(today, group.started_at)
            session_end = datetime.combine(today, group.ended_at)
            daily_minutes = int((session_end - session_start).total_seconds() / 60)

            scheduled_days = group.scheduled_day_type.values_list('name', flat=True)
            scheduled_indexes = {
                UZBEK_WEEKDAYS[day] for day in scheduled_days if day in UZBEK_WEEKDAYS
            }

            session_count = sum(
                1 for day in range(1, days_in_month + 1)
                if date(today.year, today.month, day).weekday() in scheduled_indexes
            )

            total_minutes += daily_minutes * session_count

    else:
        timelines = UserTimeLine.objects.filter(user=user)

        for timeline in timelines:
            if not timeline.start_time or not timeline.end_time:
                continue

            day_normalized = timeline.day.strip().capitalize()
            if day_normalized not in calendar.day_name:
                continue

            weekday_index = list(calendar.day_name).index(day_normalized)

            start_dt = datetime.combine(today, timeline.start_time)
            end_dt = datetime.combine(today, timeline.end_time)
            daily_minutes = int((end_dt - start_dt).total_seconds() / 60)

            work_days = [
                date(today.year, today.month, d)
                for d in range(1, days_in_month + 1)
                if date(today.year, today.month, d).weekday() == weekday_index
            ]

            total_minutes += daily_minutes * len(work_days)

    ic("Total minutesssssssss: ", total_minutes)

    per_minute_salary = round(user.salary / total_minutes, 2) if total_minutes else 0
    return {
        "total_minutes": total_minutes,
        "per_minute_salary": per_minute_salary
    }


def calculate_penalty(user_id: str, check_in: datetime, check_out: datetime = None) -> float:
    user = CustomUser.objects.filter(id=user_id).first()
    if not user or not user.salary or not check_in:
        return 0

    check_in = localize(check_in)
    if check_out:
        check_out = localize(check_out)

    check_in_date = check_in.date()
    weekday_index = check_in.weekday()
    total_penalty = 0
    per_minute_salary = get_monthly_per_minute_salary(user_id).get('per_minute_salary', 0)

    print(per_minute_salary)

    REVERSE_UZBEK_WEEKDAYS = {v: k for k, v in UZBEK_WEEKDAYS.items()}
    today_uzbek_day = REVERSE_UZBEK_WEEKDAYS.get(weekday_index)

    # === CASE 1: Teacher / Assistant
    if user.role in ["TEACHER", "ASSISTANT"] and user.calculate_penalties:
        student_groups = StudentGroup.objects.filter(
            Q(group__teacher=user) | Q(group__secondary_teacher=user),
            group__scheduled_day_type__name=today_uzbek_day
        ).select_related('group').prefetch_related('group__scheduled_day_type')

        matching_groups = []

        for sg in student_groups:
            group = sg.group
            group_start_dt = timezone.make_aware(datetime.combine(check_in.date(), group.started_at))
            delta_minutes = (check_in - group_start_dt).total_seconds() / 60
            if delta_minutes < 0:
                delta_minutes = 0

            if delta_minutes <= 60:
                matching_groups.append((group_start_dt, group, delta_minutes))

        if matching_groups:
            matching_groups.sort(key=lambda x: x[2])  # by lateness
            group_start_dt, group, late_minutes = matching_groups[0]

            if late_minutes > 0:
                penalty_amount = late_minutes * per_minute_salary
                total_penalty += penalty_amount

                bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                finance = Finance.objects.create(
                    action="EXPENSE",
                    kind=bonus_kind,
                    amount=penalty_amount,
                    stuff=user,
                    comment=f"Bugun {check_in.time()} da ishga {late_minutes} minut kechikib kelganingiz uchun {penalty_amount} sum jarima yozildi! "
                )

                print(
                    f"Late penalty for {user} at group {group.name}: {penalty_amount:.2f} ({late_minutes:.0f} min late)")

        # === Check-out Penalty
        if check_out:
            early_penalties = []

            for sg in student_groups:
                group = sg.group
                group_end_dt = localize(datetime.combine(check_out.date(), group.ended_at))

                if check_out < group_end_dt:
                    early_minutes = (group_end_dt - check_out).total_seconds() / 60
                    if early_minutes > 0:
                        penalty = early_minutes * per_minute_salary
                        early_penalties.append(penalty)

                        bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                        finance = Finance.objects.create(
                            action="EXPENSE",
                            kind=bonus_kind,
                            amount=penalty,
                            stuff=user,
                            comment=f"Bugun {check_out.time()} da ishdan  {early_minutes} minut erta ketganingiz uchun {penalty} sum jarima yozildi! "
                        )
                        print(
                            f"Early leave penalty for {user} from group {group.name}: {penalty:.2f} ({early_minutes:.0f} min early)")

            if early_penalties:
                total_penalty += max(early_penalties)

    else:

        timelines = UserTimeLine.objects.filter(user=user)

        day_name_today = calendar.day_name[weekday_index]

        matched_timeline = None

        latest_before_checkin = None

        for timeline in timelines:

            if timeline.day != day_name_today.capitalize():
                continue

            timeline_start_dt = timezone.make_aware(datetime.combine(check_in_date, timeline.start_time))

            if timeline_start_dt <= check_in:

                if not latest_before_checkin or timeline_start_dt > latest_before_checkin:
                    matched_timeline = timeline

                    latest_before_checkin = timeline_start_dt

        if matched_timeline:

            expected_start_time = matched_timeline.start_time

            timeline_start_dt = timezone.make_aware(datetime.combine(check_in_date, expected_start_time))

            # === Find the closest attendance for that day

            closest_att_time = None

            smallest_diff = None

            total_working_minutes = 0

            for att in Stuff_Attendance.objects.filter(employee=user, date=check_in_date):
                if att.check_in and att.check_out:
                    total_working_minutes += (att.check_out - att.check_in).total_seconds() // 60
                for time_field in [att.check_in, att.check_out]:

                    if not time_field:
                        continue

                    diff = abs((check_in - time_field).total_seconds())

                    if smallest_diff is None or diff < smallest_diff:
                        smallest_diff = diff

                        closest_att_time = time_field

            # === Determine actual time_diff

            if closest_att_time:

                time_diff = (check_in - closest_att_time).total_seconds() // 60

            else:

                time_diff = (check_in - timeline_start_dt).total_seconds() // 60

            ic(time_diff)

            bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()

            penalty_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Money back").first()

            # === Early Arrival Bonus

            if time_diff < 0:

                early_minutes = abs(int(time_diff))

                ic("early minutes: ", early_minutes)

                if matched_timeline.bonus:

                    bonus_amount = early_minutes * matched_timeline.bonus

                else:

                    bonus_amount = early_minutes * per_minute_salary

                ic(bonus_amount)

                total_penalty -= bonus_amount  # Subtract bonus from total penalty

                ic(total_penalty)

                Finance.objects.create(

                    action="INCOME",

                    kind=bonus_kind,

                    amount=bonus_amount,

                    stuff=user,

                    comment=f"Bugun {check_out.time()} da ishga {early_minutes} minut erta kelganingiz uchun"

                            f" {bonus_amount} sum bonus yozildi! "

                )

                print(f"Early arrival bonus for {user}: {bonus_amount:.2f} ({early_minutes} min early)")


            # === Late Arrival Penalty

            elif time_diff > 0:

                late_minutes = int(time_diff)

                if matched_timeline.penalty:

                    penalty_amount = late_minutes * matched_timeline.penalty

                else:

                    penalty_amount = late_minutes * per_minute_salary

                total_penalty += penalty_amount

                Finance.objects.create(

                    action="EXPENSE",

                    kind=penalty_kind,

                    amount=penalty_amount,

                    stuff=user,

                    comment=f"Bugun {check_in.time()} da ishga {late_minutes} minut kechikib kelganingiz uchun"

                            f" {penalty_amount} sum jarima yozildi! "

                )

                print(f"Late penalty for {user}: {penalty_amount:.2f} ({late_minutes} min late)")

            # === Early Checkout Penalty

            if check_out:

                matched_checkout_timeline = next(

                    (t for t in timelines if t.day == day_name_today.capitalize()), None

                )

                if matched_checkout_timeline:

                    expected_end_time = matched_checkout_timeline.end_time

                    timeline_end_dt = timezone.make_aware(datetime.combine(check_out.date(), expected_end_time))

                    if check_out < timeline_end_dt:
                        print(timeline_end_dt, check_out)

                        early_minutes = int((timeline_end_dt - check_out).total_seconds() // 60)

                        penalty_amount = early_minutes * per_minute_salary

                        total_penalty += penalty_amount

                        bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Money back").first()

                        Finance.objects.create(

                            action="EXPENSE",

                            kind=bonus_kind,

                            amount=penalty_amount,

                            stuff=user,

                            comment=f"Bugun {check_out.time()} da ishdan  {early_minutes} minut erta ketganingiz uchun"

                                    f" {penalty_amount} sum jarima yozildi! "

                        )

                        print(f"Employee early leave penalty: {penalty_amount:.2f} ({early_minutes} min early)")

            # === Bonus for being in office (Working Minutes Bonus)

            if total_working_minutes > 0:
                if matched_timeline and matched_timeline.bonus:
                    bonus_amount = total_working_minutes * matched_timeline.bonus
                else:
                    bonus_amount = total_working_minutes * per_minute_salary

                total_penalty -= bonus_amount  # Subtracting bonus from penalties

                Finance.objects.create(
                    action="INCOME",
                    kind=Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first(),
                    amount=bonus_amount,
                    stuff=user,
                    comment=f"Bugun {total_working_minutes} daqiqa ishda bo'lganingiz uchun {bonus_amount} sum bonus yozildi!"
                )

                print(f"Bonus for being in office: {bonus_amount:.2f} ({total_working_minutes} minutes worked)")

    return round(total_penalty, 2)
