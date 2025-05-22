import datetime

from icecream import ic

from data.finances.compensation.models import MonitoringAsos1_2, Asos1_2
from data.finances.timetracker.models import UserTimeLine


def calculate_penalty(check_in, check_out, user_id) -> float:

    timeline = UserTimeLine.objects.filter(user__id=user_id)
    day_name = datetime.datetime.today().strftime('%A')
    today = timeline.filter(day=day_name)

    if today.exists():
        ic(user_id)
        amount_obj = Asos1_2.objects.filter(
            asos="asos1",
            type="Compensation"
        ).first()
        ic(amount_obj)
        if not amount_obj:
            return 0.0

        delta = check_out - check_in
        minutes = delta.total_seconds() / 60
        ic(minutes)

        if minutes > 0:
            return minutes * amount_obj.amount
    return 0.0

