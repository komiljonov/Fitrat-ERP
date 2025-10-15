from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.db.models import QuerySet


if TYPE_CHECKING:
    from data.student.course.models import Course
    from data.student.subject.models import Level
    from data.student.groups.models import Day
    from data.student.groups.models import Group

from data.student.subject.models import Theme

UZBEK_WEEKDAYS = [
    "Dushanba",
    "Seshanba",
    "Chorshanba",
    "Payshanba",
    "Juma",
    "Shanba",
    "Yakshanba",
]


def calculate_finish_date(
    course: "Course",
    level: "Level",
    week_days: "QuerySet[Day]",
    start_date: date,
    number_of_repeated_lessons: int = 0,
):

    themes = Theme.objects.filter(course=course, level=level, is_archived=False)
    total_lessons = themes.count() + number_of_repeated_lessons

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


def _group_weekdays(group: "Group") -> list[int]:
    """
    Return sorted list of weekday indices (1=Mon..7=Sun) for the group's scheduled days.
    """
    return sorted(group.scheduled_day_type.values_list("index", flat=True))


def next_lesson_date(from_date, weekdays: list[int]):
    """
    Given a date and a list of weekdays (1=Mon..7=Sun),
    return the next scheduled date strictly after from_date.
    """
    if not weekdays:
        return None

    weekdays = sorted(weekdays)  # ensure order
    wd = from_date.isoweekday()  # Monday=1..Sunday=7

    # Compute deltas (1..7), never 0 so we always move forward
    deltas = [((w - wd) % 7) or 7 for w in weekdays]
    return from_date + timedelta(days=min(deltas))
