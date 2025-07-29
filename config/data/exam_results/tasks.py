# tasks.py

from celery import shared_task

from data.exam_results.models import UnitTest
from data.notifications.models import Notification
from data.student.studentgroup.models import StudentGroup


@shared_task
def send_unit_test_notification(unit_test_id, group_id):
    unit_test = UnitTest.objects.filter(id=unit_test_id).prefetch_related("themes").first()
    if not unit_test:
        return

    print("Tasks started -----------------------")

    group_students = StudentGroup.objects.filter(group_id=group_id).select_related("student__user", "group__teacher")
    theme_names = ", ".join(t.name for t in unit_test.themes.all())

    for gs in group_students:
        student = gs.student
        Notification.objects.create(
            user=student.user,
            comment=(
                f"{student.first_name} {student.last_name} siz uchun "
                f"{theme_names} fanlaridan Unit test belgilangan."
            ),
            come_from=unit_test.id,
            choice="Examination",
        )

    # Notify the teacher once
    if group_students.exists():
        group = group_students.first().group
        teacher = group.teacher
        if teacher:
            Notification.objects.create(
                user=teacher,
                comment=(
                    f"{teacher.full_name} sizning {group.name} guruhingiz uchun "
                    f"{theme_names} fanlaridan Unit test belgilangan."
                ),
                come_from=unit_test.id,
                choice="Examination",
            )
