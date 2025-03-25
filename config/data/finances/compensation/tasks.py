import logging
from datetime import datetime
from ...student.studentgroup.models import StudentGroup
from celery import shared_task

from .models import StudentCountMonitoring, Monitoring5
from ...account.models import CustomUser

logging.basicConfig(level=logging.INFO)

@shared_task
def check_monthly_student_catching_monitoring():
    counts = StudentCountMonitoring.objects.all()
    for count in counts:
        for teacher in CustomUser.objects.filter(role="TEACHER"):
            student_count = StudentGroup.objects.filter(group_teacher=teacher).count()
            if student_count >= count.from_point and student_count <= count.to_point:
                monitoring = Monitoring5.objects.create(
                    teacher = teacher,
                    student_count = student_count,
                    ball=count.max_ball,
                )

                if monitoring:
                    logging.info("Asos 5 uchun monitoring utkazildi!....")


