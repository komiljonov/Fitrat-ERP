from celery import shared_task

from data.student.attendance.models import Attendance
from data.student.studentgroup.models import StudentGroup


@shared_task
def check_for_streak_students():

    students = StudentGroup.objects.filter(is_archived=False)

    for student in students:
        pass
