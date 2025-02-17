from django.shortcuts import render
from rest_framework.generics import ListAPIView

from data.finances.finance.models import Finance
from data.lid.new_lid.models import Lid
from data.student.attendance.models import Attendance
from data.student.student.models import Student
from data.student.studentgroup.models import StudentGroup


class DashboardView(ListAPIView):
    orders = Lid.objects.filter(
        is_archived=False,
        is_frozen=False,
        lid_stage_type="ORDERED_LID"
    ).count()
    orders_archived = Lid.objects.filter(
        is_archived=True,
        is_frozen=False,
        lid_stage_type="ORDERED_LID",
    ).count()
    first_lesson = Lid.objects.filter(
        is_archived=False,
        is_frozen=False,
        lid_stage_type="ORDERED_LID",
        ordered_stages="BIRINCHI_DARS_BELGILANGAN"
    ).count()
    first_lesson_archived = Lid.objects.filter(
        is_archived=False,
        is_frozen=False,
        lid_stage_type="ORDERED_LID",
        ordered_stages="BIRINCHI_DARSGA_KELMAGAN"
    ).count()
    first_lesson_come = Lid.objects.filter(
        is_archived=True,
        is_frozen=False,
        lid_stage_type="ORDERED_LID",
        ordered_stages="BIRINCHI_DARS_BELGILANGAN"
    ).count()
    first_lesson_come_archived=35
    first_course_payment = Finance.objects.filter(
        action="INCOME",
        kind="COURSE_PAYMENT",
        is_first=True,
    ).count()
    first_course_payment_archived = Finance.objects.filter(
        action="INCOME",
        kind="COURSE_PAYMENT",
        is_first=True,
        student__is_archived=True,  # Assuming 'student' is a foreign key to the Student model
    ).count()

    course_ended = StudentGroup.objects.filter(
        group__status="INACTIVE",
    ).count()
    moved_to_filial=45
    come_from_filial=13

    data = {
        "orders": orders,
        "orders_archived": orders_archived,
        "first_lesson": first_lesson,
        "first_lesson_come": first_lesson_come,
        "first_lesson_come_archived": first_lesson_come_archived,
        "first_course_payment": first_course_payment,
        "first_course_payment_archived": first_course_payment_archived,
        "course_ended": course_ended,
        "moved_to_filial": moved_to_filial,
        "come_from_filial": come_from_filial,
    }




