from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db.models import QuerySet


if TYPE_CHECKING:
    from data.student.course.models import Course
    from data.student.subject.models import Level
    from data.student.groups.models import Day


UZBEK_WEEKDAYS = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]

from data.student.subject.models import Theme


def calculate_finish_date(
    course: "Course", level: "Level", week_days: QuerySet[Day], start_date: date
):

    themes = Theme.objects.filter(course=course, level=level, is_archived=False)
    total_lessons = themes.count()

    scheduled_days = [
        UZBEK_WEEKDAYS.index(day.name)
        for day in week_days
        if day.name in UZBEK_WEEKDAYS
    ]

    if not scheduled_days:
        return  # Can't calculate finish date without schedule

    finish_date = start_date
    lessons_scheduled = 0

    while lessons_scheduled < total_lessons:
        if finish_date.weekday() in scheduled_days:
            lessons_scheduled += 1
        finish_date += timedelta(days=1)

    return finish_date
