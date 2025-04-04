import logging
from datetime import datetime, timedelta
from celery import shared_task
from django.utils.timezone import now
from icecream import ic

from ..lesson.models import ExtraLesson
from ..student.models import Student
from ..studentgroup.models import StudentGroup
from ...account.models import CustomUser
from ...finances.compensation.models import Bonus, Compensation
from ...finances.finance.models import KpiFinance
from ...teachers import teacher

logging.basicConfig(level=logging.INFO)

@shared_task
def check_monthly_extra_lessons():
    today = now().date()

    start_of_month = today.replace(day=1)

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


@shared_task
def check_accountant_kpi():
    today = now().date()

    start_of_month = today.replace(day=1)  # First day of the month
    next_month = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
    end_of_month = next_month - timedelta(days=1)  # Last day of the current month

    # Get accountants for each filial
    accountants = CustomUser.objects.filter(role="ACCOUNTING")

    for accountant in accountants:
        # Get active students with no debt
        active_students = Student.objects.filter(balance_status="ACTIVE", student_stage_type="ACTIVE_STUDENT")

        if active_students.count() > 0:
            bonuses = Bonus.objects.filter(user=accountant, name="Har bir qarzdor bo’lmagan va Aktiv o'quvchi uchun bonus")

            for bonus in bonuses:
                total_kpi = active_students.count() * bonus.amount
                for student in active_students:
                    KpiFinance.objects.create(
                        user=accountant,
                        student=student,
                        type=f"{start_of_month.month} oyi uchun {active_students.count()} ta active"
                             f" va qarzdor bulmagan o'quvchi uchun {total_kpi} sum bonus!",
                        amount=total_kpi
                    )

                logging.info(f"📊 Monthly Task: {total_kpi} for {active_students.count()} no-debt active students for {accountant}")


        students = Student.objects.filter(is_archived=False,)

        if students.count() > 0:
            active_no_debt_students = students.filter(balance__gte=300000)
            new_no_debt_students = students.filter(balance_status="ACTIVE", balance__gte=0)

            active_percentage = ((active_no_debt_students.count() + new_no_debt_students.count()) / students.count()) * 100

            if active_percentage <95:
                bonus = Bonus.objects.filter(user=accountant,name="Jami yangi va aktiv o'quvchi o'quvchilarning "
                                                                  "93% dan 94.9% gacha bo'lgan qismi uchun bonus").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami yangi va aktiv o'quvchi o'quvchilarning "
                                                                  "93% dan 94.9% gacha bo'lgan qismi uchun bonus",
                    amount=bonus.amount,
                    type="INCOME",
                )

            if active_percentage == 100:
                bonus = Bonus.objects.filter(user=accountant, name="Jami yangi va aktiv o'quvchi o'quvchilarning "
                                                                   "100% gacha bo'lgan qismi uchun bonus").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami yangi va aktiv o'quvchi o'quvchilarning "
                                                                   "100% gacha bo'lgan qismi uchun bonus",
                    amount=bonus.amount,
                    type="INCOME",
                )

            if active_percentage >= 98 and active_percentage <= 99.9:
                bonus = Bonus.objects.filter(user=accountant, name="Jami yangi va aktiv o'quvchi o'quvchilarning"
                                                                   " 98% dan 99.9% gacha bo'lgan qismi uchun bonus").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami yangi va aktiv o'quvchi o'quvchilarning 98% dan 99.9% gacha bo'lgan qismi uchun bonus",
                    amount=bonus.amount,
                    type="INCOME",
                )

            if active_percentage >=95 and active_percentage <=97.9:
                bonus = Bonus.objects.filter(user=accountant, name="Jami yangi va aktiv o'quvchi o'quvchilarning "
                                                                   "95% dan 97.9% gacha bo'lgan qismi uchun bonus").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami yangi va aktiv o'quvchi o'quvchilarning 95% dan 97.9% gacha bo'lgan qismi uchun bonus",
                    amount=bonus.amount,
                    type="INCOME",
                )

        debt = Student.objects.filter(balance_status="INACTIVE",balance__lte=0, is_archived=False)
        if debt.count() > 0:
            debt_percentage = (debt.count() / students.count()) * 100

            if debt_percentage > 0 and debt_percentage <= 70:
                comp = Compensation.objects.filter(user=accountant, name="Jami qarzdor o'quvchilar sonining "
                                                                         "70% dan kichik bo'lgan qismi (Jarima)").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami qarzdor o'quvchilar sonining 70% dan kichik bo'lgan qismi (Jarima)",
                    amount=comp.amount,
                    type="EXPENSE",
                )

            if debt_percentage >=70.1 and debt_percentage <=80:
                comp = Compensation.objects.filter(user=accountant, name="Jami qarzdor o'quvchilar sonining 70% "
                                                                         "dan 80.1% gacha bo'lgan qismi (Jarima)").first()
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami qarzdor o'quvchilar sonining 70% dan 80.1% gacha bo'lgan qismi (Jarima)",
                    amount=comp.amount,
                    type="EXPENSE",
                )

            if debt_percentage >=80.1 and debt_percentage <=85:
                comp = Compensation.objects.filter(user=accountant,name="Jami qarzdor o'quvchilar sonining"
                                                                        " 80.1% dan 85% gacha bo'lgan qismi (Jarima)")
                KpiFinance.objects.create(
                    user=accountant,
                    lid=None,
                    student=None,
                    reason="Jami qarzdor o'quvchilar sonining 80.1% dan 85% gacha bo'lgan qismi (Jarima)",
                    amount=comp.amount,
                    type="EXPENSE",
                )

        logging.info(f"for {accountant.full_name} months kpi calculation ended ... ")
    logging.info(f"months kpi calculation ended ... ")


@shared_task
def check_monitoring_manager_kpi():
    att_manager = CustomUser.objects.filter(role="ATTENDANCE_MANAGER")
    for manager in att_manager:
        bonus = Bonus.objects.filter(user=manager, name="Aktiv o'quvchi soniga bonus").first()
        if bonus and bonus.amount > 0 and manager is not None:
            # Loop through each filial if it's a ManyToManyField
            for filial in manager.filial.all():  # Iterating over each related filial
                students = Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT",
                    balance_status="ACTIVE",
                    filial__id=filial.id  # Access the id of the related filial
                )
                KpiFinance.objects.create(
                    user=manager,
                    reason="Aktiv o'quvchi soniga bonus",
                    amount=(bonus.amount * students.count()) if bonus else 0,
                    type="INCOME",
                    lid=None,
                    student=None
                )


@shared_task
def check_filial_manager_kpi():
    att_manager = CustomUser.objects.filter(role="FILIAL_Manager")
    for manager in att_manager:
        bonus = Bonus.objects.filter(user=manager, name="Aktiv o'quvchi soniga bonus").first()
        if bonus and bonus.amount > 0 and manager is not None:
            # Loop through each filial if it's a ManyToManyField
            for filial in manager.filial.all():  # Iterating over each related filial
                students = Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT",
                    balance_status="ACTIVE",
                    filial__id=filial.id  # Access the id of the related filial
                )
                KpiFinance.objects.create(
                    user=manager,
                    reason="Aktiv o'quvchi soniga bonus",
                    amount=(bonus.amount * students.count()) if bonus else 0,
                    type="INCOME",
                    lid=None,
                    student=None
                )


@shared_task
def check_filial_director_kpi():
    att_manager = CustomUser.objects.filter(role="HEAD_TEACHER")
    for manager in att_manager:
        bonus = Bonus.objects.filter(user=manager, name="Aktiv o'quvchi soniga bonus").first()
        if bonus and bonus.amount > 0 and manager is not None:
            # Loop through each filial if it's a ManyToManyField
            for filial in manager.filial.all():  # Iterating over each related filial
                students = Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT",
                    balance_status="ACTIVE",
                    filial__id=filial.id  # Access the id of the related filial
                )
                KpiFinance.objects.create(
                    user=manager,
                    reason="Aktiv o'quvchi soniga bonus",
                    amount=(bonus.amount * students.count()) if bonus else 0,
                    type="INCOME",
                    lid=None,
                    student=None
                )


@shared_task
def check_monitoring_manager_kpi():
    att_manager = CustomUser.objects.filter(role="MONITORING_MANAGER")
    for manager in att_manager:
        bonus = Bonus.objects.filter(user=manager, name="Aktiv o'quvchi soniga bonus").first()
        if bonus and bonus.amount > 0 and manager is not None:
            # Loop through each filial if it's a ManyToManyField
            for filial in manager.filial.all():  # Iterating over each related filial
                students = Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT",
                    balance_status="ACTIVE",
                    filial__id=filial.id  # Access the id of the related filial
                )
                KpiFinance.objects.create(
                    user=manager,
                    reason="Aktiv o'quvchi soniga bonus",
                    amount=(bonus.amount * students.count()) if bonus else 0,
                    type="INCOME",
                    lid=None,
                    student=None
                )


@shared_task
def check_testolog_manager_kpi():
    att_manager = CustomUser.objects.filter(role="TESTOLOG")
    for manager in att_manager:
        bonus = Bonus.objects.filter(user=manager, name="Aktiv o'quvchi soniga bonus").first()
        if bonus and bonus.amount > 0 and manager is not None:
            # Loop through each filial if it's a ManyToManyField
            for filial in manager.filial.all():  # Iterating over each related filial
                students = Student.objects.filter(
                    student_stage_type="ACTIVE_STUDENT",
                    balance_status="ACTIVE",
                    filial__id=filial.id  # Access the id of the related filial
                )
                KpiFinance.objects.create(
                    user=manager,
                    reason="Aktiv o'quvchi soniga bonus",
                    amount=(bonus.amount * students.count()) if bonus else 0,
                    type="INCOME",
                    lid=None,
                    student=None
                )
