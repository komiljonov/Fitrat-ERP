import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils.timezone import now
from ..lesson.models import ExtraLesson
from ..studentgroup.models import StudentGroup
from ...finances.finance.models import KpiFinance
from ...teachers import teacher

logging.basicConfig(level=logging.INFO)

@shared_task
def check_monthly_extra_lessons():
    today = now().date()

    start_of_month = today.replace(day=1)  # First day of the month

    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)  # Last day of the current month

    extra_lessons = ExtraLesson.objects.filter(date__gte=start_of_month, date__lte=end_of_month)

    teachers = extra_lessons.values_list('teacher', flat=True).distinct()

    logging.info(f"📅 Monthly Task: Found {extra_lessons.count()} extra lessons for {today.strftime('%B %Y')}.")
    logging.info(f"👨‍🏫 Teachers involved: {list(teachers)}")

    for lesson in extra_lessons:
        if lesson.is_payable == True:
            group = StudentGroup.objects.filter(group__teacher=lesson.teacher,student=lesson.student,
                                                group__status="ACTIVE").first()
            if group:
                KpiFinance.objects.create(
                    user=lesson.teacher,
                    lid=None,
                    student=lesson.student,
                    type=f"{lesson.date.strftime('%d %m %Y')} da {lesson.student.first_name} {lesson.student.last_name} "
                         f"uchun tashkil qilingan qo'shimcha dars uchun bonus",
                )




    return list(teachers)
