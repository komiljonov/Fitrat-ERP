import datetime

from data.finances.timetracker.models import UserTimeLine


def calculate_penalty(check_in, check_out, user_id) -> float:
    # Get current day name (e.g., Monday)
    day_name = datetime.datetime.today().strftime('%A')

    try:
        timeline = UserTimeLine.objects.get(user_id=user_id, day=day_name)
    except UserTimeLine.DoesNotExist:
        return 0

    if timeline.start_time:
        timeline_start_minutes = timeline.start_time.hour * 60 + timeline.start_time.minute
        check_in_minutes = check_in.hour * 60 + check_in.minute

        late_minutes = check_in_minutes - timeline_start_minutes
        if late_minutes > 0:
            penalty = late_minutes * 10000
            return penalty
    return 0
