from celery import shared_task

from data.student.studentgroup.models import StudentGroup
from data.logs.models import Log


@shared_task
def check_for_streak_students():

    students = StudentGroup.objects.filter(is_archived=False).exclude(student=None)

    for student in students:

        streak = student.streak()

        if (student.student.status == "NEW_STUDENT" and streak == 3) or (
            student.student.status == "ACTIVE_STUDENT" and streak == 5
        ):

            student.is_archived = True
            student.save()

            Log.object.create(
                object="STUDENT",
                action="STUDENT_GROUP_ARCHIVED",
                comment=f"O'quvchi {streak} kun darslarga kelmagani uchun, guruhdan chetlashtirildi.",
                student=student.student,
            )

            if student.student.groups.filter(is_archived=False).count() == 1:
                student.student.is_archived = True
                student.student.save()

                Log.object.create(
                    object="STUDENT",
                    action="STUDENT_ARCHIVED",
                    comment=f"O'quvchi {streak} kun darslarga kelmagani uchun, archivelandi.",
                )
