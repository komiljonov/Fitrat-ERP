from datetime import datetime, timedelta

from celery import shared_task

from data.notifications.models import Notification
from data.student.quiz.models import Exam

@shared_task
def handle_task_creation(exam_id):
    exam = Exam.objects.filter(id=exam_id).first()
    if exam:
        now = datetime.now()
        exam_start_datetime = datetime.combine(exam.date, exam.start_time)

        # If less than 12 hours remain before the exam starts
        if exam_start_datetime - now <= timedelta(hours=12):
            exam.status = "Inactive"
            exam.save()