from data.finances.timetracker.models import UserTimeLine


def build_weekly_schedule(user):
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    schedule = {}

    for day in days:
        timeline = UserTimeLine.objects.filter(user=user, day=day).first()
        schedule[f"wt_{day.lower()}"] = {
            "start": timeline.start_time.strftime("%H:%M") if timeline else "09:00",
            "end": timeline.end_time.strftime("%H:%M") if timeline else "18:00",
        }

    return schedule