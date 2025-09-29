from typing import Any
from django.core.management.base import BaseCommand
from tqdm import tqdm

from data.student.attendance.models import Attendance
from data.student.studentgroup.models import StudentGroup


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> str | None:

        attendances = Attendance.objects.filter(student_group=None)

        for attendance in tqdm(attendances):

            sg = StudentGroup.objects.filter(
                student=attendance.student,
                lid=attendance.lead,
                group=attendance.group,
            ).first()

            attendance.student_group = sg
            attendance.save()
