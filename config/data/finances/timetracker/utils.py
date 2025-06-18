import calendar
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import List

import pytz
from django.db.models import Q
from django.utils.timezone import make_aware, is_aware
from icecream import ic
from rest_framework.exceptions import ValidationError

from data.account.models import CustomUser
from data.finances.finance.models import Finance, Kind
from data.finances.timetracker.models import UserTimeLine
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from data.finances.timetracker.views import AttendanceError
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
    user = CustomUser.objects.select_related().filter(id=user_id).first()
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
            group_start_dt = localize(datetime.combine(check_in.date(), group.started_at))
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
        min_diff = timedelta(hours=1)

        for timeline in timelines:
            if timeline.day != day_name_today.capitalize():
                continue

            timeline_start_dt = localize(datetime.combine(check_in_date, timeline.start_time))

            if check_in >= timeline_start_dt:
                time_diff = check_in - timeline_start_dt
                if not matched_timeline or time_diff < (
                        check_in - localize(datetime.combine(check_in_date, matched_timeline.start_time))):
                    matched_timeline = timeline

        if matched_timeline:
            expected_start_time = matched_timeline.start_time
            timeline_start_dt = localize(datetime.combine(check_in_date, expected_start_time))

            time_diff = (check_in - timeline_start_dt).total_seconds() // 60

            ic(time_diff)

            bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
            penalty_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Money back").first()

            # === Early Arrival Bonus
            if time_diff < 0:
                early_minutes = abs(int(time_diff))
                early_minutes += 23
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
                    comment=f"Bugun {check_in.time()} da ishga {early_minutes} minut erta kelganingiz uchun"
                            f" {bonus_amount} sum bonus yozildi! "
                )
                print(f"Early arrival bonus for {user}: {bonus_amount:.2f} ({early_minutes} min early)")

            # === Late Arrival Penalty
            elif time_diff > 0:
                late_minutes = int(time_diff)
                late_minutes += 23
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

        if check_out:
            matched_checkout_timeline = next(
                (t for t in timelines if t.day == day_name_today.capitalize()), None
            )

            if matched_checkout_timeline:
                expected_end_time = matched_checkout_timeline.end_time
                timeline_end_dt = localize(datetime.combine(check_out.date(), expected_end_time))

                if check_out < timeline_end_dt:
                    early_minutes = int((timeline_end_dt - check_out).total_seconds() // 60)
                    early_minutes += 23
                    penalty_amount = early_minutes * per_minute_salary
                    total_penalty += penalty_amount
                    bonus_kind = Kind.objects.filter(action="EXPENSE", name__icontains="Bonus").first()
                    finance = Finance.objects.create(
                        action="EXPENSE",
                        kind=bonus_kind,
                        amount=penalty_amount,
                        stuff=user,
                        comment=f"Bugun {check_in.time()} da ishdan  {early_minutes} minut erta ketganingiz uchun"
                                f" {penalty_amount} sum jarima yozildi! "
                    )
                    print(f"Employee early leave penalty: {penalty_amount:.2f} ({early_minutes} min early)")

    return round(total_penalty, 2)



def parse_datetime_string(value):
    try:
        # Fix the format: replace underscore with dash if needed
        value = value.replace('_', '-')
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        raise ValidationError(f"Invalid datetime format: {value}") from e


# def get_affective_time_amount(user_id,check_in, check_out):
#     user = CustomUser.objects.filter(id=user_id).first()
#
#     if not user:
#         return 0
#
#     user


# Utility functions for error handling
def safe_decimal_conversion(value, field_name: str) -> Decimal:
    """Safely convert value to Decimal with error handling"""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as e:
        raise AttendanceError(
            f"Invalid numeric value for {field_name}",
            "INVALID_NUMERIC_VALUE",
            {'field': field_name, 'value': value, 'error': str(e)}
        )



def validate_time_sequence(actions: List[dict]) -> None:
    """Validate that action times make logical sense"""
    for i in range(len(actions) - 1):
        current_end = actions[i]['end_datetime']
        next_start = actions[i + 1]['start_datetime']

        if current_end > next_start:
            raise AttendanceError(
                f"Time overlap detected between actions {i + 1} and {i + 2}",
                "TIME_OVERLAP_ERROR",
                {
                    'action1_end': actions[i]['end'],
                    'action2_start': actions[i + 1]['start']
                }
            )



class AttendanceErrorHandler:
    """Centralized error handling for attendance operations"""

    @staticmethod
    def handle_validation_error(error: ValidationError) -> dict:
        """Handle DRF validation errors"""
        return {
            'error': 'Validation failed',
            'error_code': 'VALIDATION_ERROR',
            'details': error.detail if hasattr(error, 'detail') else str(error)
        }

    @staticmethod
    def handle_database_error(error: Exception) -> dict:
        """Handle database-related errors"""
        return {
            'error': 'Database operation failed',
            'error_code': 'DATABASE_ERROR',
            'details': {'message': str(error)}
        }

    @staticmethod
    def handle_calculation_error(error: Exception) -> dict:
        """Handle calculation-related errors"""
        return {
            'error': 'Calculation failed',
            'error_code': 'CALCULATION_ERROR',
            'details': {'message': str(error)}
        }



def update_calculate(user_id: str, check_in: datetime, check_out: datetime = None) -> float:
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
            group_start_dt = localize(datetime.combine(check_in.date(), group.started_at))
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

            if early_penalties:
                total_penalty += max(early_penalties)

    else:
        timelines = UserTimeLine.objects.filter(user=user)
        day_name_today = calendar.day_name[weekday_index]

        matched_timeline = None
        min_diff = timedelta(hours=1)

        for timeline in timelines:
            if timeline.day != day_name_today.capitalize():
                continue

            timeline_start_dt = localize(datetime.combine(check_in_date, timeline.start_time))

            if check_in >= timeline_start_dt:
                time_diff = check_in - timeline_start_dt
                if not matched_timeline or time_diff < (
                        check_in - localize(datetime.combine(check_in_date, matched_timeline.start_time))):
                    matched_timeline = timeline

        if matched_timeline:
            expected_start_time = matched_timeline.start_time
            timeline_start_dt = localize(datetime.combine(check_in_date, expected_start_time))

            time_diff = (check_in - timeline_start_dt).total_seconds() // 60

            if time_diff < 0:
                early_minutes = abs(int(time_diff))
                early_minutes += 23
                ic("early minutes: ", early_minutes)

                if matched_timeline.bonus:
                    bonus_amount = early_minutes * matched_timeline.bonus
                else:
                    bonus_amount = early_minutes * per_minute_salary

                ic(bonus_amount)

                total_penalty -= bonus_amount


            elif time_diff > 0:
                late_minutes = int(time_diff)
                late_minutes += 23
                if matched_timeline.penalty:
                    penalty_amount = late_minutes * matched_timeline.penalty
                else:
                    penalty_amount = late_minutes * per_minute_salary

                total_penalty += penalty_amount


        if check_out:
            matched_checkout_timeline = next(
                (t for t in timelines if t.day == day_name_today.capitalize()), None
            )

            if matched_checkout_timeline:
                expected_end_time = matched_checkout_timeline.end_time
                timeline_end_dt = localize(datetime.combine(check_out.date(), expected_end_time))

                if check_out < timeline_end_dt:
                    early_minutes = int((timeline_end_dt - check_out).total_seconds() // 60)
                    early_minutes += 23
                    penalty_amount = early_minutes * per_minute_salary
                    total_penalty += penalty_amount


    return round(total_penalty, 2)
