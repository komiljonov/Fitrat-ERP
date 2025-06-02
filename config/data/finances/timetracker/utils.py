import calendar
from datetime import date, datetime, timedelta

from django.db.models import Q
from django.utils.timezone import make_aware, is_aware, get_default_timezone
from icecream import ic

from data.account.models import CustomUser
from data.finances.timetracker.models import UserTimeLine
from data.student.groups.models import Group
from data.student.studentgroup.models import StudentGroup

UZBEK_WEEKDAYS = {
    'Dushanba': 0,
    'Seshanba': 1,
    'Chorshanba': 2,
    'Payshanba': 3,
    'Juma': 4,
    'Shanba': 5,
    'Yakshanba': 6
}

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
        # === Regular employee using timeline
        timelines = UserTimeLine.objects.filter(user=user)

        for timeline in timelines:
            if not timeline.start_time or not timeline.end_time:
                continue

            # Normalize and validate timeline.day
            day_normalized = timeline.day.strip().capitalize()
            if day_normalized not in calendar.day_name:
                continue  # Skip invalid day names

            weekday_index = list(calendar.day_name).index(day_normalized)

            # Calculate daily work duration in minutes
            start_dt = datetime.combine(today, timeline.start_time)
            end_dt = datetime.combine(today, timeline.end_time)
            daily_minutes = int((end_dt - start_dt).total_seconds() / 60)

            # Count matching weekdays in this month
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


def calculate_penalty(user_id: int, check_in: datetime, check_out: datetime = None) -> float:

    tz = get_default_timezone()
    user = CustomUser.objects.filter(id=user_id).first()
    if not user or not user.salary or not check_in:
        return 0

    # Normalize check_in to Tashkent timezone
    if not is_aware(check_in):
        check_in = make_aware(check_in, timezone=tz)
    else:
        check_in = check_in.astimezone(tz)

    if check_out:
        if not is_aware(check_out):
            check_out = make_aware(check_out, timezone=tz)
        else:
            check_out = check_out.astimezone(tz)

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
            group_start_dt = datetime.combine(check_in.date(), group.started_at)
            group_start_dt = make_aware(group_start_dt, timezone=tz) if not is_aware(group_start_dt) else group_start_dt.astimezone(tz)

            delta_minutes = (check_in - group_start_dt).total_seconds() / 60
            if delta_minutes < 0:
                delta_minutes = 0

            if delta_minutes <= 60:
                matching_groups.append((group_start_dt, group, delta_minutes))

        if matching_groups:
            matching_groups.sort(key=lambda x: x[2])  # sort by lateness
            group_start_dt, group, late_minutes = matching_groups[0]

            if late_minutes > 0:
                penalty_amount = late_minutes * per_minute_salary
                total_penalty += penalty_amount
                print(f"Late penalty for {user} at group {group.name}: {penalty_amount:.2f} ({late_minutes:.0f} min late)")

        # === Check-out Penalty for Teacher
        if check_out:
            early_penalties = []

            for sg in student_groups:
                group = sg.group
                group_end_dt = datetime.combine(check_out.date(), group.ended_at)
                group_end_dt = make_aware(group_end_dt, timezone=tz) if not is_aware(group_end_dt) else group_end_dt.astimezone(tz)

                if check_out < group_end_dt:
                    early_minutes = (group_end_dt - check_out).total_seconds() / 60
                    if early_minutes > 0:
                        penalty = early_minutes * per_minute_salary

                        early_penalties.append(penalty)
                        print(f"Early leave penalty for {user} from group {group.name}: {penalty:.2f} ({early_minutes:.0f} min early)")

            if early_penalties:
                total_penalty += max(early_penalties)  # only apply the most serious violation

    else:
        timelines = UserTimeLine.objects.filter(user=user)
        day_name_today = calendar.day_name[weekday_index]  # e.g., 'Monday'
        ic(day_name_today.capitalize())

        # Initialize for potential match
        matched_timeline = None
        min_diff = timedelta(hours=1)

        for timeline in timelines:
            if timeline.day != day_name_today.capitalize():
                continue

            timeline_start_dt = datetime.combine(check_in_date, timeline.start_time)
            timeline_start_dt = make_aware(timeline_start_dt, timezone=tz) if not is_aware(
                timeline_start_dt) else timeline_start_dt.astimezone(tz)

            if check_in >= timeline_start_dt and (check_in - timeline_start_dt) <= min_diff:
                time_diff = check_in - timeline_start_dt

                if matched_timeline:
                    prev_diff = check_in - datetime.combine(check_in_date, matched_timeline.start_time)
                    if time_diff < prev_diff:
                        matched_timeline = timeline
                else:
                    matched_timeline = timeline

        # Calculate Check-in penalty if matched
        if matched_timeline:
            ic(matched_timeline)

            expected_start_time = matched_timeline.start_time
            timeline_start_dt = datetime.combine(check_in_date, expected_start_time)
            timeline_start_dt = make_aware(timeline_start_dt, timezone=tz) if not is_aware(
                timeline_start_dt) else timeline_start_dt.astimezone(tz)

            late_minutes = int((check_in - timeline_start_dt).total_seconds() // 60)
            ic(late_minutes)

            penalty_amount = late_minutes * per_minute_salary
            total_penalty += penalty_amount
            ic(f"Employee late penalty: {penalty_amount:.2f} ({late_minutes} min late)")

        # Check-out Penalty (same as before but ensure correct matching)
        matched_checkout_timeline = next(
            (t for t in timelines if t.day == day_name_today),
            None
        )

        if check_out and matched_checkout_timeline:
            expected_end_time = matched_checkout_timeline.end_time
            timeline_end_dt = datetime.combine(check_out.date(), expected_end_time)
            timeline_end_dt = make_aware(timeline_end_dt, timezone=tz) if not is_aware(
                timeline_end_dt) else timeline_end_dt.astimezone(tz)

            if check_out < timeline_end_dt:
                early_minutes = int((timeline_end_dt - check_out).total_seconds() // 60)
                penalty_amount = early_minutes * per_minute_salary
                total_penalty += penalty_amount
                print(f"Employee early leave penalty: {penalty_amount:.2f} ({early_minutes} min early)")


    return round(total_penalty, 2)
