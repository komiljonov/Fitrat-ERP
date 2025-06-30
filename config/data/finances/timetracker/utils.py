import calendar
import decimal
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

# FIXED DELETE FUNCTION:

def delete_user_actions(user, actions, date):
    """Delete existing actions for the given date"""

    # Convert date string to date object if needed
    if isinstance(date, str):
        date = datetime.fromisoformat(date + "T00:00:00").date()

    # Get daily attendance record
    daily_att = Employee_attendance.objects.filter(
        employee=user,
        date=date,
    ).first()

    if daily_att:
        # Delete all finance records for this date
        Finance.objects.filter(
            stuff=user,
            created_at__date=date
        ).delete()

        # Delete all attendance records for this date
        Stuff_Attendance.objects.filter(
            employee=user,
            date=date,
        ).delete()

        # Reset daily attendance amount
        daily_att.amount = 0
        daily_att.save()

        print(f"Deleted all attendance records for {date}")

    return 0


def delete_user_finances(user, daily_att):


    finances = Finance.objects.filter(
        stuff=user,
        amount=daily_att.amount,
        created_at__date=daily_att.date
    ).first()

    if finances:

        daily_att.amount = 0
        daily_att.save()

        ic(finances)

        if finances.amount is None:
            amount = decimal.Decimal("0")
        else:
            amount = finances.amount

        user.balance -= amount
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


def calculate_amount(user, actions):
    if not actions:
        return {"total_eff_amount": 0}

    check_in_date = datetime.fromisoformat(actions[0]["start"]).date()
    weekday_index = check_in_date.weekday()

    user_penalty = get_user_penalty(user, check_in_date)
    user_bonus = get_user_bonus(user, check_in_date)

    REVERSE_UZBEK_WEEKDAYS = {v: k for k, v in UZBEK_WEEKDAYS.items()}
    today_uzbek_day = REVERSE_UZBEK_WEEKDAYS.get(weekday_index)

    # Delete existing finance records for this date to avoid duplicates
    Finance.objects.filter(
        stuff=user,
        created_at__date=check_in_date,
        comment__contains=str(check_in_date)
    ).delete()

    penalty_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Money back").first()
    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()

    total_eff_amount = 0

    # === CASE 1: Teacher / Assistant
    if user.role in ["TEACHER", "ASSISTANT"] and user.calculate_penalties:
        total_eff_amount = calculate_teacher_amount(
            user, actions, check_in_date, today_uzbek_day,
            user_bonus, user_penalty, penalty_kind, bonus_kind
        )
    else:
        total_eff_amount = calculate_regular_amount(
            user, actions, check_in_date,
            user_bonus, user_penalty, penalty_kind, bonus_kind
        )

    return {"total_eff_amount": total_eff_amount}


def calculate_teacher_amount(user, actions, check_in_date, today_uzbek_day,
                             user_bonus, user_penalty, penalty_kind, bonus_kind):
    student_groups = StudentGroup.objects.filter(
        Q(group__teacher=user) | Q(group__secondary_teacher=user),
        group__scheduled_day_type__name=today_uzbek_day
    ).select_related('group').prefetch_related('group__scheduled_day_type')

    matching_groups = []
    for period in student_groups:
        if period.group.started_at and period.group.ended_at:
            dt_start = datetime.combine(check_in_date, period.group.started_at)
            dt_end = datetime.combine(check_in_date, period.group.ended_at)
            matching_groups.append(Range(dt_start, dt_end))

    if not matching_groups:
        return 0

    # Calculate effective work time
    include_ranges = [
        Range(
            datetime.fromisoformat(a["start"]),
            datetime.fromisoformat(a["end"])
        )
        for a in actions
    ]

    effective_times = include_only_ranges(matching_groups, include_ranges)
    total_minutes = int(effective_times.total_seconds() / 60)
    total_eff_amount = total_minutes * user_bonus

    # Calculate penalties and bonuses
    sorted_actions = sorted(actions, key=lambda a: a["start"])
    first_action = sorted_actions[0]
    last_action = sorted_actions[-1]  # Get the LAST action

    first_timeline = min(student_groups, key=lambda sg: sg.group.started_at or datetime.max.time())
    last_timeline = max(student_groups, key=lambda sg: sg.group.ended_at or datetime.min.time())

    # Early arrival bonus / Late arrival penalty
    first_action_dt = datetime.fromisoformat(first_action.get("start"))
    first_timeline_dt = datetime.combine(check_in_date, first_timeline.group.started_at)

    arrive_diff = (first_action_dt - first_timeline_dt).total_seconds() / 60

    if arrive_diff < 0:  # Early arrival
        comment = f"{check_in_date} sanasida ishga {abs(arrive_diff):.0f} minut erta kelganingiz uchun bonus."
        amount = abs(arrive_diff) * user_bonus
        Finance.objects.create(
            action="EXPENSE", amount=amount, stuff=user,
            kind=bonus_kind, comment=comment
        )
    elif arrive_diff > 0:  # Late arrival
        comment = f"{check_in_date} sanasida ishga {arrive_diff:.0f} minut kech kelganingiz uchun jarima."
        amount = arrive_diff * user_penalty
        Finance.objects.create(
            action="EXPENSE", amount=-amount, stuff=user,
            kind=penalty_kind, comment=comment
        )

    # Early departure penalty / Late departure bonus
    last_action_dt = datetime.fromisoformat(last_action.get("end"))  # Use 'end' not 'start'
    last_timeline_dt = datetime.combine(check_in_date, last_timeline.group.ended_at)

    depart_diff = (last_timeline_dt - last_action_dt).total_seconds() / 60

    if depart_diff > 0:  # Early departure
        comment = f"{check_in_date} sanasida ishdan {depart_diff:.0f} minut erta ketganingiz uchun jarima."
        amount = depart_diff * user_penalty
        Finance.objects.create(
            action="EXPENSE", amount=-amount, stuff=user,
            kind=penalty_kind, comment=comment
        )
    elif depart_diff < 0:  # Late departure
        comment = f"{check_in_date} sanasida ishdan {abs(depart_diff):.0f} minut kech ketganingiz uchun bonus."
        amount = abs(depart_diff) * user_bonus
        Finance.objects.create(
            action="EXPENSE", amount=amount, stuff=user,
            kind=bonus_kind, comment=comment
        )

    # Work time bonus
    if total_eff_amount > 0:
        comment = f"{check_in_date} sanasida {total_minutes} minut ishda bulganingiz uchun bonus."
        Finance.objects.create(
            action="EXPENSE", amount=total_eff_amount, stuff=user,
            kind=bonus_kind, comment=comment
        )

    return total_eff_amount


def calculate_regular_amount(user, actions, check_in_date,
                             user_bonus, user_penalty, penalty_kind, bonus_kind):
    day = check_in_date.strftime('%A')
    timelines = UserTimeLine.objects.filter(user=user, day=day).all()

    if not timelines:
        return 0

    main_ranges = []
    for period in timelines:
        if period.start_time and period.end_time:
            dt_start = datetime.combine(check_in_date, period.start_time)
            dt_end = datetime.combine(check_in_date, period.end_time)
            main_ranges.append(Range(dt_start, dt_end))

    # Calculate effective work time
    include_ranges = [
        Range(
            datetime.fromisoformat(a["start"]),
            datetime.fromisoformat(a["end"])
        )
        for a in actions
    ]

    effective_times = include_only_ranges(main_ranges, include_ranges)
    total_minutes = int(effective_times.total_seconds() / 60)
    total_eff_amount = total_minutes * user_bonus

    # Calculate penalties and bonuses
    sorted_actions = sorted(actions, key=lambda a: a["start"])
    first_action = sorted_actions[0]
    last_action = sorted_actions[-1]

    first_timeline = timelines.order_by("start_time").first()
    last_timeline = timelines.order_by("-end_time").first()  # Order by end_time

    # Early arrival bonus / Late arrival penalty
    first_action_dt = datetime.fromisoformat(first_action.get("start"))
    first_timeline_dt = datetime.combine(check_in_date, first_timeline.start_time)

    arrive_diff = (first_action_dt - first_timeline_dt).total_seconds() / 60

    if arrive_diff < 0:  # Early arrival
        comment = f"{check_in_date} sanasida ishga {abs(arrive_diff):.0f} minut erta kelganingiz uchun bonus."
        amount = abs(arrive_diff) * user_bonus
        Finance.objects.create(
            action="EXPENSE", amount=amount, stuff=user,
            kind=bonus_kind, comment=comment
        )
    elif arrive_diff > 0:  # Late arrival
        comment = f"{check_in_date} sanasida ishga {arrive_diff:.0f} minut kech kelganingiz uchun jarima."
        amount = arrive_diff * user_penalty
        Finance.objects.create(
            action="EXPENSE", amount=-amount, stuff=user,
            kind=penalty_kind, comment=comment
        )

    # Early departure penalty / Late departure bonus
    last_action_dt = datetime.fromisoformat(last_action.get("end"))  # Use 'end' not 'start'
    last_timeline_dt = datetime.combine(check_in_date, last_timeline.end_time)  # Use end_time

    depart_diff = (last_timeline_dt - last_action_dt).total_seconds() / 60

    if depart_diff > 0:  # Early departure
        comment = f"{check_in_date} sanasida ishdan {depart_diff:.0f} minut erta ketganingiz uchun jarima."
        amount = depart_diff * user_penalty
        Finance.objects.create(
            action="EXPENSE", amount=-amount, stuff=user,
            kind=penalty_kind, comment=comment
        )
    elif depart_diff < 0:  # Late departure
        comment = f"{check_in_date} sanasida ishdan {abs(depart_diff):.0f} minut kech ketganingiz uchun bonus."
        amount = abs(depart_diff) * user_bonus
        Finance.objects.create(
            action="EXPENSE", amount=amount, stuff=user,
            kind=bonus_kind, comment=comment
        )

    # Work time bonus
    if total_eff_amount > 0:
        comment = f"{check_in_date} sanasida {total_minutes} minut ishda bulganingiz uchun bonus."
        Finance.objects.create(
            action="EXPENSE", amount=total_eff_amount, stuff=user,
            kind=bonus_kind, comment=comment
        )

    return total_eff_amount





# ADDITIONAL HELPER FUNCTION:

def validate_actions_data(actions):
    """Validate that actions data is properly formatted"""

    if not actions or not isinstance(actions, list):
        return False, "Actions must be a non-empty list"

    for action in actions:
        if not isinstance(action, dict):
            return False, "Each action must be a dictionary"

        required_fields = ['start', 'end', 'type']
        for field in required_fields:
            if field not in action:
                return False, f"Action missing required field: {field}"

        # Validate datetime strings
        try:
            datetime.fromisoformat(action['start'])
            datetime.fromisoformat(action['end'])
        except ValueError:
            return False, "Invalid datetime format in action"

    return True, "Valid"