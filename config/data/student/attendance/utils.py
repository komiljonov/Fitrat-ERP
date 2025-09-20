from typing import TYPE_CHECKING
from datetime import date as _date

from django.db.models import Subquery, Value, DateField
from django.db.models.functions import Coalesce
from django.core.exceptions import ValidationError


from data.student.attendance.choices import AttendanceStatusChoices
from data.student.groups.models import Group


if TYPE_CHECKING:
    from data.lid.new_lid.models import Lid
    from data.student.student.models import Student


ABSENCE_NEUTRAL = {
    AttendanceStatusChoices.UNREASONED,  # counts
    AttendanceStatusChoices.REASONED,  # neutral: doesn't count, doesn't break
}


def current_streak(
    group: "Group",
    *,
    student: "Student | None" = None,
    lead: "Lid | None" = None,
) -> int:
    """
    Current streak of UNREASONED absences for either a Student OR a Lid.
    Keyword-only. Exactly one of (student, lead) must be provided.
    """
    # from data.student.attendance.models import Attendance
    from data.lid.new_lid.models import Lid
    from data.student.student.models import Student

    if (student is None and lead is None) or (student is not None and lead is not None):
        raise ValidationError(
            "Provide exactly one of 'student' or 'lead' (keyword-only)."
        )

    if student is not None and not isinstance(student, Student):
        raise ValidationError("'student' must be a Student instance.")

    if lead is not None and not isinstance(lead, Lid):
        raise ValidationError("'lead' must be a Lid instance.")

    base_filter = {"student": student} if student is not None else {"lead": lead}

    last_break_date_sq = (
        group.attendances.filter(**base_filter)
        .exclude(status__in=ABSENCE_NEUTRAL)  # breakers: e.g., COME/IS_PRESENT/LATE/...
        .order_by("-date")
        .values("date")[:1]
    )

    print(last_break_date_sq)

    default_old_date = _date(1900, 1, 1)

    return group.attendances.filter(
        **base_filter,
        # status__in=[AttendanceStatusChoices.UNREASONED, AttendanceStatusChoices.EMPTY],
        date__gt=Coalesce(
            Subquery(last_break_date_sq),
            Value(default_old_date, output_field=DateField()),
        ),
    ).count()
