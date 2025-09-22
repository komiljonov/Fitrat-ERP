from celery import shared_task

from django.utils import timezone
from django.db.models import Q

from data.student.studentgroup.models import StudentGroup
from data.logs.models import Log

from django.db import transaction


@shared_task
def check_for_streak_students():

    today = timezone.now().date()

    with transaction.atomic():

        students = StudentGroup.objects.filter(
            is_archived=False, student__isnull=False
        ).exclude(  # skip groups without student
            Q(student__is_frozen=True) & Q(student__frozen_days__gte=today)
        )

        for sg in students:

            streak = sg.streak()

            print(f"{sg.student.first_name} {sg.student.last_name} - {streak}")

            if (sg.student.status == "NEW_STUDENT" and streak >= 3) or (
                sg.student.status == "ACTIVE_STUDENT" and streak >= 5
            ):

                sg.is_archived = True
                sg.save()

                print(
                    f"Kicket {sg.student.first_name} {sg.student.last_name} from group:{sg.group.name}, streak is: {streak}"
                )

                Log.objects.create(
                    object="STUDENT",
                    action="STUDENT_GROUP_ARCHIVED",
                    comment=f"O'quvchi {streak} kun darslarga kelmagani uchun, guruhdan chetlashtirildi.",
                    student=sg.student,
                    student_group=sg,
                )

                if sg.student.groups.filter(is_archived=False).count() == 1:
                    sg.student.is_archived = True
                    sg.student.save()

                    Log.objects.create(
                        object="STUDENT",
                        action="STUDENT_ARCHIVED",
                        comment=f"O'quvchi {streak} kun darslarga kelmagani uchun, archivelandi.",
                        student=sg.student,
                        student_group=sg,
                    )

                    print(
                        f"Archived student: {sg.student.first_name} {sg.student.last_name}"
                    )
