import calendar
from datetime import date, time
from datetime import datetime, timedelta
from typing import List

import pytz
from django.db.models import Q
from django.utils import timezone
from django.utils.timezone import make_aware, is_aware
from icecream import ic

from data.account.models import CustomUser
from data.finances.finance.models import Finance, Kind
from data.finances.timetracker.delta import include_only_ranges, Range
from data.finances.timetracker.models import UserTimeLine, Stuff_Attendance, Employee_attendance
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


def get_updated_datas(user, date):
    user_attendances = Stuff_Attendance.objects.filter(employee=user, date=date)

    all_actions = []

    for att in user_attendances:
        if isinstance(att.actions, list):
            all_actions.extend(att.actions)

    all_actions.sort(key=lambda a: a.get("start"))

    return all_actions


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


def delete_user_actions(user, actions):
    for action in actions:
        date = datetime.fromisoformat(action.get("start")).date()

        daily_att = Employee_attendance.objects.filter(
            employee=user,
            date=date,
        ).first()

        if daily_att:
            daily_att.amount = 0
            daily_att.save()

        att = Stuff_Attendance.objects.filter(
            employee=user,
            check_in=action.get('start'),
            check_out=action.get('end'),
            date=date,
        ).first()

        if att:
            delete_finance = delete_user_finances(user, att)
            if delete_finance == 0:
                print(f"att {att.check_in} finance amount {att.amount} sum deleted...")

            att.delete()
            print(f"Deleted {action.get('start')} attendance")

    return 0


def delete_user_finances(user, attendance):
    if not isinstance(attendance, Stuff_Attendance):
        raise ValueError(f"Expected Stuff_Attendance instance, got: {attendance}")

    finances = Finance.objects.filter(
        stuff=user,
        amount=attendance.amount,
        created_at__date=attendance.date
    ).first()

    if finances:

        user.balance -= finances.amount
        user.save()

        finances.delete()

        return 0
    else:
        return 1


def get_user_bonus(user, date):
    day = date.strftime('%A')

    timeline = UserTimeLine.objects.filter(user=user)

    per_minute_salary = get_monthly_per_minute_salary(user.id).get('per_minute_salary', 0)

    for period in timeline:
        if period.bonus:
            return period.bonus
    else:
        return per_minute_salary


def get_user_penalty(user, date):
    day = date.strftime('%A')

    timeline = UserTimeLine.objects.filter(user=user)

    per_minute_salary = get_monthly_per_minute_salary(user.id).get('per_minute_salary', 0)

    for period in timeline:
        if period.penalty:
            return period.penalty
    else:
        return per_minute_salary


# def get_effective_times(user, actions: List[dict]):
#     from datetime import date as Date
#
#     start_dt = actions[0].get("start")
#     if isinstance(start_dt, str):
#         start_dt = datetime.fromisoformat(start_dt)
#
#     action_date: Date = start_dt.date()
#     day = action_date.strftime('%A')
#
#     timeline = UserTimeLine.objects.filter(user=user, day=day).all()
#
#     results = []
#
#
#     for action in actions:
#         start = action.get("start")
#         end = action.get("end")
#
#         if isinstance(start, str):
#             start = datetime.fromisoformat(start)
#         if isinstance(end, str):
#             end = datetime.fromisoformat(end)
#
#         for period in timeline:
#             period_start = datetime.combine(action_date, period.start_time)
#             period_end = datetime.combine(action_date, period.end_time)
#             if period_end <= period_start:
#                 period_end += timedelta(days=1)
#
#             if end <= period_start or start >= period_end:
#                 continue
#
#             effective_start = max(start, period_start)
#             effective_end = min(end, period_end)
#             effective_duration = (effective_end - effective_start).total_seconds() / 60
#
#             penalty_duration = max(0, (period_start - start).total_seconds() / 60)
#             bonus_duration = max(0, (end - period_end).total_seconds() / 60)
#
#             results.append({
#                 "period_start": period_start.time(),
#                 "period_end": period_end.time(),
#                 "effective_start": effective_start.time(),
#                 "effective_end": effective_end.time(),
#                 "action_start": start,
#                 "action_end": end,
#                 "effective_minutes": int(effective_duration),
#                 "penalty_minutes": int(penalty_duration),
#                 "bonus_minutes": int(bonus_duration),
#             })
#
#     total_effective = sum(r["effective_minutes"] for r in results)
#     total_penalty = sum(r["penalty_minutes"] for r in results)
#     total_bonus = sum(r["bonus_minutes"] for r in results)
#
#     return {
#         "total_effective_minutes": total_effective,
#         "total_penalty_minutes": total_penalty,
#         "total_bonus_minutes": total_bonus,
#         "details": results
#     }


def calculate_amount(user, actions):
    check_in_date = datetime.fromisoformat(actions[0]["start"]).date()

    weekday_index = check_in_date.weekday()

    user_penalty = get_user_penalty(user, check_in_date)
    user_bonus = get_user_bonus(user, check_in_date)

    REVERSE_UZBEK_WEEKDAYS = {v: k for k, v in UZBEK_WEEKDAYS.items()}
    today_uzbek_day = REVERSE_UZBEK_WEEKDAYS.get(weekday_index)

    # === CASE 1: Teacher / Assistant
    # if user.role in ["TEACHER", "ASSISTANT"] and user.calculate_penalties:
    #     student_groups = StudentGroup.objects.filter(
    #         Q(group__teacher=user) | Q(group__secondary_teacher=user),
    #         group__scheduled_day_type__name=today_uzbek_day
    #     ).select_related('group').prefetch_related('group__scheduled_day_type')
    #
    #     matching_groups = []
    #
    #     for sg in student_groups:
    #         group = sg.group
    #         group_start_dt = timezone.make_aware(datetime.combine(check_in.date(), group.started_at))
    #         delta_minutes = (check_in - group_start_dt).total_seconds() / 60
    #         if delta_minutes < 0:
    #             delta_minutes = 0
    #
    #         if delta_minutes <= 60:
    #             matching_groups.append((group_start_dt, group, delta_minutes))
    #
    #     if matching_groups:
    #         matching_groups.sort(key=lambda x: x[2])  # by lateness
    #         group_start_dt, group, late_minutes = matching_groups[0]
    #
    #         if late_minutes > 0:
    #             penalty_amount = late_minutes * per_minute_salary
    #             total_penalty += penalty_amount
    #
    #             bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
    #             finance = Finance.objects.create(
    #                 action="EXPENSE",
    #                 kind=bonus_kind,
    #                 amount=penalty_amount,
    #                 stuff=user,
    #                 comment=f"{check_in.date()} - {check_in.time()} da ishga {late_minutes :.2f} minut kechikib kelganingiz uchun {penalty_amount:.2f} sum jarima yozildi! "
    #             )
    #
    #             print(
    #                 f"Late penalty for {user} at group {group.name}: {penalty_amount:.2f} ({late_minutes:.0f} min late)")
    #
    #     # === Check-out Penalty
    #     if check_out:
    #         early_penalties = []
    #
    #         for sg in student_groups:
    #             group = sg.group
    #             group_end_dt = localize(datetime.combine(check_out.date(), group.ended_at))
    #
    #             if check_out < group_end_dt:
    #                 early_minutes = (group_end_dt - check_out).total_seconds() / 60
    #                 if early_minutes > 0:
    #                     penalty = early_minutes * per_minute_salary
    #                     early_penalties.append(penalty)
    #
    #                     bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
    #                     finance = Finance.objects.create(
    #                         action="EXPENSE",
    #                         kind=bonus_kind,
    #                         amount=penalty,
    #                         stuff=user,
    #                         comment=f"{check_in.date()} - {check_out.time()} da ishdan  {early_minutes:.2f} minut erta ketganingiz uchun {penalty:.2f} sum jarima yozildi! "
    #                     )
    #                     print(
    #                         f"Early leave penalty for {user} from group {group.name}: {penalty:.2f} ({early_minutes:.0f} min early)")
    #
    #         if early_penalties:
    #             total_penalty += max(early_penalties)

    # else:


    day = check_in_date.strftime('%A')

    timelines = UserTimeLine.objects.filter(user=user, day=day).all()

    def ensure_date(value):
        if isinstance(value, date):
            return value
        return datetime.fromisoformat(value).date()

    # Main loop
    main_ranges = []
    for period in timelines:
        if period.start_time and period.end_time:
            period_day = ensure_date(check_in_date)

            if isinstance(period.start_time, time):
                dt_start = datetime.combine(period_day, period.start_time)
            else:
                dt_start = period.start_time

            if isinstance(period.end_time, time):
                dt_end = datetime.combine(period_day, period.end_time)
            else:
                dt_end = period.end_time

            main_ranges.append(Range(dt_start, dt_end))

    include_ranges = [
        Range(
            datetime.fromisoformat(a["start"]),
            datetime.fromisoformat(a["end"])
        )
        for a in actions
    ]

    effective_times = include_only_ranges(main_ranges, include_ranges)

    print(effective_times)

    total_effective_minutes = effective_times * 60


    total_eff_amount: float = total_effective_minutes * user_bonus

    penalty_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Money back").first()
    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()

    date = actions[0].get("start")
    if isinstance(date, str):
        date = datetime.fromisoformat(date)

    if total_eff_amount > 0:
        comment = (f"{date.date()} sanasida"
                   f" {total_effective_minutes} minut ishda bulganingiz uchun bonus.")

        finance = Finance.objects.create(
            action="EXPENSE",
            amount=total_eff_amount,
            stuff=user,
            kind=bonus_kind,
            comment=comment
        )


    return {
        "total_eff_amount": total_eff_amount,
    }
