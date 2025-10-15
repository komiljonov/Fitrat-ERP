import datetime

from celery import shared_task

from .models import Student


@shared_task
def update_frozen_status():
    today = datetime.datetime.today()
    frozen_students = Student.objects.filter(frozen_till_date=today)
    for student in frozen_students:
        student.is_frozen = False
        student.save()