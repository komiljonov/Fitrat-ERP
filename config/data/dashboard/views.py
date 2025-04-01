from collections import defaultdict
from datetime import datetime, timedelta
from io import BytesIO

import pandas as pd
from django.db.models import Case, When
from django.db.models import Count
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import ExtractWeekDay, Concat
from django.http import HttpResponse
from django.utils.dateparse import parse_date
from icecream import ic
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance, Casher, Kind, SaleStudent, VoucherStudent
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room, Group, Day
from data.student.studentgroup.models import StudentGroup
from ..account.models import CustomUser
from ..lid.new_lid.serializers import LidSerializer
from ..results.models import Results
from ..student.attendance.models import Attendance
from ..student.lesson.models import FirstLLesson
from ..student.student.models import Student
from ..upload.serializers import FileUploadSerializer


class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        # Get Query Parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        channel_id = request.query_params.get('marketing_channel')
        service_manager = request.query_params.get('service_manager')
        call_operator = request.query_params.get('call_operator')
        sales_manager = request.query_params.get('sales_manager')
        filial = request.query_params.get('filial')
        subjects = request.query_params.get('subject')
        course = request.query_params.get('course')
        teacher = request.query_params.get('teacher')
        is_student = request.query_params.get('is_student')

        # Common Filters
        filters = {}
        if start_date and end_date is "":
            filters["created_at__date"] = start_date
        if start_date and end_date:
            filters["created_at__gte","created_at__lte"] = start_date,end_date
        if filial:
            filters["filial"] = filial

        # Initial QuerySets
        lid = Lid.objects.filter(**filters)
        archived_lid = lid.filter(lid_stage_type="NEW_LID",is_archived=True)
        orders = lid.filter(lid_stage_type="ORDERED_LID")
        orders_archived = orders.filter(is_archived=True)
        first_lesson = FirstLLesson.objects.filter(**filters)

        # Students with One Attendance
        students_with_one_attendance = Attendance.objects.values("student").annotate(
            count=Count("id")).filter(count=1, **filters).values_list("student", flat=True)

        first_lesson_come = Student.objects.filter(id__in=students_with_one_attendance, **filters)
        first_lesson_come_archived = first_lesson_come.filter(is_archived=True)

        # First Course Payment Students
        payment_students = Finance.objects.filter(
            student__isnull=False, kind__name="COURSE_PAYMENT", **filters
        ).values_list("student", flat=True)

        first_course_payment = Student.objects.filter(id__in=payment_students, **filters)
        first_course_payment_archived = first_course_payment.filter(is_archived=True)

        # Active and Ended Courses
        new_student = StudentGroup.objects.filter(student__student_stage_type="NEW_STUDENT", **filters)
        active_student = StudentGroup.objects.filter(student__student_stage_type="ACTIVE_STUDENT",group__status="ACTIVE", **filters)
        course_ended = StudentGroup.objects.filter(group__status="INACTIVE", **filters)

        # **Filtering Based on Dynamic Conditions**

        if is_student:
            is_student_value = is_student.capitalize()

            lid = lid.filter(is_student=is_student_value, is_archived=False)
            archived_lid = archived_lid.filter(is_student=is_student_value)
            orders = orders.filter(is_student=is_student_value,is_archived=False)
            orders_archived = orders_archived.filter(is_student=is_student_value)
            first_lesson = first_lesson.filter(lid__is_student=is_student_value, lid__is_archived=False)
            first_lesson_come = first_lesson_come.filter(is_archived=False)

            first_lesson_come_archived = first_lesson_come.filter(
                is_archived=True) if first_lesson_come.exists() else None
            first_course_payment = first_course_payment.filter(is_archived=is_student_value)
            first_course_payment_archived = first_course_payment.filter(
                is_archived=True) if first_course_payment.exists() else None

        if channel_id:
            channel = MarketingChannel.objects.get(id=channel_id)
            lid = lid.filter(marketing_channel=channel)
            archived_lid = archived_lid.filter(marketing_channel=channel)
            orders = orders.filter(marketing_channel=channel)
            orders_archived = orders_archived.filter(marketing_channel=channel)
            first_lesson = first_lesson.filter(lid__marketing_channel=channel)
            first_lesson_come = first_lesson_come.filter(marketing_channel=channel)
            first_lesson_come_archived = first_lesson_come_archived.filter(marketing_channel=channel)
            first_course_payment = first_course_payment.filter(marketing_channel=channel)
            first_course_payment_archived = first_course_payment_archived.filter(marketing_channel=channel)

        if service_manager:
            lid = lid.filter(service_manager_id=service_manager)
            archived_lid = archived_lid.filter(service_manager_id=service_manager)
            orders = orders.filter(service_manager_id=service_manager)
            orders_archived = orders_archived.filter(service_manager_id=service_manager)
            first_lesson = first_lesson.filter(lid__service_manager_id=service_manager)
            first_lesson_come = first_lesson_come.filter(service_manager_id=service_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(service_manager_id=service_manager)
            first_course_payment = first_course_payment.filter(service_manager_id=service_manager)
            first_course_payment_archived = first_course_payment_archived.filter(service_manager_id=service_manager)

        if sales_manager:
            lid = lid.filter(sales_manager_id=sales_manager)
            archived_lid = archived_lid.filter(sales_manager_id=sales_manager)
            orders = orders.filter(sales_manager_id=sales_manager)
            orders_archived = orders_archived.filter(sales_manager_id=sales_manager)
            first_lesson = first_lesson.filter(lid__sales_manager_id=sales_manager)
            first_lesson_come = first_lesson_come.filter(sales_manager_id=sales_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(sales_manager_id=sales_manager)
            first_course_payment = first_course_payment.filter(sales_manager_id=sales_manager)
            first_course_payment_archived = first_course_payment_archived.filter(sales_manager_id=sales_manager)

        if call_operator:
            lid = lid.filter(call_operator_id=call_operator)
            archived_lid = archived_lid.filter(call_operator_id=call_operator)
            orders = orders.filter(call_operator_id=call_operator)
            orders_archived = orders_archived.filter(call_operator_id=call_operator)
            first_lesson = first_lesson.filter(lid__call_operator_id=call_operator)
            first_lesson_come = first_lesson_come.filter(call_operator_id=call_operator)
            first_lesson_come_archived = first_lesson_come_archived.filter(call_operator_id=call_operator)
            first_course_payment = first_course_payment.filter(call_operator_id=call_operator)
            first_course_payment_archived = first_course_payment_archived.filter(call_operator_id=call_operator)

        if subjects:
            lid = lid.filter(subject_id=subjects)
            archived_lid = archived_lid.filter(subject_id=subjects)
            orders = orders.filter(subject_id=subjects)
            orders_archived = orders_archived.filter(subject_id=subjects)
            first_lesson = first_lesson.filter(lid__subject_id=subjects)
            first_lesson_come = first_lesson_come.filter(subject_id=subjects)
            first_lesson_come_archived = first_lesson_come_archived.filter(subject_id=subjects)
            first_course_payment = first_course_payment.filter(subject_id=subjects)
            first_course_payment_archived = first_course_payment_archived.filter(subject_id=subjects)

        if teacher:
            lid = lid.filter(lids_group__group__teacher_id=teacher)
            archived_lid = archived_lid.filter(lids_group__group__teacher_id=teacher)
            orders = orders.filter(lids_group__group__teacher_id=teacher)
            orders_archived = orders_archived.filter(lids_group__group__teacher_id=teacher)
            first_lesson = first_lesson.filter(group__teacher_id=teacher)
            first_lesson_come = first_lesson_come.filter(students_group__group__teacher_id=teacher)
            first_lesson_come_archived = first_lesson_come_archived.filter(students_group__group_id=teacher)
            first_course_payment = first_course_payment.filter(students_group__group__teacher_id=teacher)
            first_course_payment_archived = first_course_payment_archived.filter(students_group__group__teacher_id=teacher)

        if course:
            lid = lid.filter(lids_group__group__course_id=course)
            archived_lid = archived_lid.filter(lids_group__group__course_id=course)
            orders = orders.filter(lids_group__group__course_id=course)
            orders_archived = orders_archived.filter(lids_group__group__course_id=course)
            first_lesson = first_lesson.filter(group__course_id=course)
            first_lesson_come = first_lesson_come.filter(students_group__group__course_id=course)
            first_lesson_come_archived = first_lesson_come_archived.filter(students_group__group__course_id=course)
            first_course_payment = first_course_payment.filter(students_group__group__course_id=course)
            first_course_payment_archived = first_course_payment_archived.filter(students_group__group__course_id=course)

        # Final Data Output
        data = {
            "lids": lid.count(),
            "archived_lid": archived_lid.count(),
            "orders": orders.count(),
            "orders_archived": orders_archived.count(),
            "first_lesson": first_lesson.count(),
            "first_lesson_come": first_lesson_come.count(),
            "first_lesson_come_archived": first_lesson_come_archived.count() if first_lesson_come_archived else 0,
            "first_course_payment": first_course_payment.count(),
            "new_student": new_student.count(),
            "active_student": active_student.count(),
            "first_course_payment_archived": first_course_payment_archived.count() if first_course_payment_archived else 0,
            "course_ended": course_ended.count(),
        }

        return Response(data)


class DashboardSecondView(APIView):
    def get(self, request, *args, **kwargs):
        # Get Query Parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        channel_id = request.query_params.get('marketing_channel')
        service_manager = request.query_params.get('service_manager')
        call_operator = request.query_params.get('call_operator')
        sales_manager = request.query_params.get('sales_manager')
        filial = request.query_params.get('filial')
        subjects = request.query_params.get('subject')
        course = request.query_params.get('course')
        teacher = request.query_params.get('teacher')
        is_student = request.query_params.get('is_student')

        # Common Filters
        filters = {}
        if start_date:
            filters["created_at__gte"] = start_date
        if end_date:
            filters["created_at__lte"] = end_date
        if filial:
            filters["filial_id"] = filial

        # Initial QuerySets
        lid = Lid.objects.filter(lid_stage_type="NEW_LID",**filters).exclude(ordered_stages="BIRINCHI_DARS_BELGILANGAN")
        archived_lid = lid.filter(lid_stage_type="NEW_LID",is_archived=True,)
        orders = lid.filter(lid_stage_type="ORDERED_LID")
        orders_archived = orders.filter(is_archived=True)
        first_lesson = FirstLLesson.objects.filter(**filters)

        # Students with One Attendance
        students_with_one_attendance = Attendance.objects.values("student").annotate(
            count=Count("id")).filter(count=1, **filters).values_list("student", flat=True)

        first_lesson_come = Student.objects.filter(id__in=students_with_one_attendance, **filters)
        first_lesson_come_archived = first_lesson_come.filter(is_archived=True)

        # First Course Payment Students
        payment_students = Finance.objects.filter(
            student__isnull=False, kind__name="COURSE_PAYMENT", **filters
        ).values_list("student", flat=True)

        first_course_payment = Student.objects.filter(id__in=payment_students, **filters)
        first_course_payment_archived = first_course_payment.filter(is_archived=True)

        # Active and Ended Courses
        new_student = Student.objects.filter(student_stage_type="NEW_STUDENT", **filters)
        active_student = Student.objects.filter(student_stage_type="ACTIVE_STUDENT", **filters)
        course_ended = StudentGroup.objects.filter(group__status="INACTIVE", **filters)
        all_students = Student.objects.filter(is_archived=False)

        # **Filtering Based on Dynamic Conditions**

        if is_student:
            is_student_value = is_student.capitalize()

            lid = lid.filter(is_student=is_student_value, is_archived=False)
            archived_lid = archived_lid.filter(is_student=is_student_value)
            orders = orders.filter(is_student=is_student_value,is_archived=False)
            orders_archived = orders_archived.filter(is_student=is_student_value)
            first_lesson = first_lesson.filter(lid__is_student=is_student_value, lid__is_archived=False)
            first_lesson_come = first_lesson_come.filter(is_archived=False)

            first_lesson_come_archived = first_lesson_come.filter(
                is_archived=True) if first_lesson_come.exists() else None
            first_course_payment = first_course_payment.filter(is_archived=is_student_value)
            first_course_payment_archived = first_course_payment.filter(
                is_archived=True) if first_course_payment.exists() else None

        if channel_id:
            channel = MarketingChannel.objects.get(id=channel_id)
            lid = lid.filter(marketing_channel=channel)
            archived_lid = archived_lid.filter(marketing_channel=channel)
            orders = orders.filter(marketing_channel=channel)
            orders_archived = orders_archived.filter(marketing_channel=channel)
            first_lesson = first_lesson.filter(lid__marketing_channel=channel)
            first_lesson_come = first_lesson_come.filter(marketing_channel=channel)
            first_lesson_come_archived = first_lesson_come_archived.filter(marketing_channel=channel)
            first_course_payment = first_course_payment.filter(marketing_channel=channel)
            first_course_payment_archived = first_course_payment_archived.filter(marketing_channel=channel)

        if service_manager:
            lid = lid.filter(service_manager_id=service_manager)
            archived_lid = archived_lid.filter(service_manager_id=service_manager)
            orders = orders.filter(service_manager_id=service_manager)
            orders_archived = orders_archived.filter(service_manager_id=service_manager)
            first_lesson = first_lesson.filter(lid__service_manager_id=service_manager)
            first_lesson_come = first_lesson_come.filter(service_manager_id=service_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(service_manager_id=service_manager)
            first_course_payment = first_course_payment.filter(service_manager_id=service_manager)
            first_course_payment_archived = first_course_payment_archived.filter(service_manager_id=service_manager)

        if sales_manager:
            lid = lid.filter(sales_manager_id=sales_manager)
            archived_lid = archived_lid.filter(sales_manager_id=sales_manager)
            orders = orders.filter(sales_manager_id=sales_manager)
            orders_archived = orders_archived.filter(sales_manager_id=sales_manager)
            first_lesson = first_lesson.filter(lid__sales_manager_id=sales_manager)
            first_lesson_come = first_lesson_come.filter(sales_manager_id=sales_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(sales_manager_id=sales_manager)
            first_course_payment = first_course_payment.filter(sales_manager_id=sales_manager)
            first_course_payment_archived = first_course_payment_archived.filter(sales_manager_id=sales_manager)

        if call_operator:
            lid = lid.filter(call_operator_id=call_operator)
            archived_lid = archived_lid.filter(call_operator_id=call_operator)
            orders = orders.filter(call_operator_id=call_operator)
            orders_archived = orders_archived.filter(call_operator_id=call_operator)
            first_lesson = first_lesson.filter(lid__call_operator_id=call_operator)
            first_lesson_come = first_lesson_come.filter(call_operator_id=call_operator)
            first_lesson_come_archived = first_lesson_come_archived.filter(call_operator_id=call_operator)
            first_course_payment = first_course_payment.filter(call_operator_id=call_operator)
            first_course_payment_archived = first_course_payment_archived.filter(call_operator_id=call_operator)

        if subjects:
            lid = lid.filter(subject_id=subjects)
            archived_lid = archived_lid.filter(subject_id=subjects)
            orders = orders.filter(subject_id=subjects)
            orders_archived = orders_archived.filter(subject_id=subjects)
            first_lesson = first_lesson.filter(lid__subject_id=subjects)
            first_lesson_come = first_lesson_come.filter(subject_id=subjects)
            first_lesson_come_archived = first_lesson_come_archived.filter(subject_id=subjects)
            first_course_payment = first_course_payment.filter(subject_id=subjects)
            first_course_payment_archived = first_course_payment_archived.filter(subject_id=subjects)

        if teacher:
            lid = lid.filter(lids_group__group__teacher_id=teacher)
            archived_lid = archived_lid.filter(lids_group__group__teacher_id=teacher)
            orders = orders.filter(lids_group__group__teacher_id=teacher)
            orders_archived = orders_archived.filter(lids_group__group__teacher_id=teacher)
            first_lesson = first_lesson.filter(group__teacher_id=teacher)
            first_lesson_come = first_lesson_come.filter(students_group__group__teacher_id=teacher)
            first_lesson_come_archived = first_lesson_come_archived.filter(students_group__group_id=teacher)
            first_course_payment = first_course_payment.filter(students_group__group__teacher_id=teacher)
            first_course_payment_archived = first_course_payment_archived.filter(students_group__group__teacher_id=teacher)

        if course:
            lid = lid.filter(lids_group__group__course_id=course)
            archived_lid = archived_lid.filter(lids_group__group__course_id=course)
            orders = orders.filter(lids_group__group__course_id=course)
            orders_archived = orders_archived.filter(lids_group__group__course_id=course)
            first_lesson = first_lesson.filter(group__course_id=course)
            first_lesson_come = first_lesson_come.filter(students_group__group__course_id=course)
            first_lesson_come_archived = first_lesson_come_archived.filter(students_group__group__course_id=course)
            first_course_payment = first_course_payment.filter(students_group__group__course_id=course)
            first_course_payment_archived = first_course_payment_archived.filter(students_group__group__course_id=course)

        # Final Data Output
        data = {
            "lids": lid.count(),
            "archived_lid": archived_lid.count(),
            "archive_lid_res" : LidSerializer(lid, many=True).data,
            "orders": orders.count(),
            "orders_archived": orders_archived.count(),
            "first_lesson": first_lesson.count(),
            "first_lesson_come": first_lesson_come.count(),
            "first_lesson_come_archived": first_lesson_come_archived.count() if first_lesson_come_archived else 0,
            "first_course_payment": first_course_payment.count(),
            "new_student": new_student.count(),
            "active_student": active_student.count(),
            "first_course_payment_archived": first_course_payment_archived.count() if first_course_payment_archived else 0,
            "course_ended": course_ended.count(),
            "all_students": all_students.count(),
        }

        return Response(data)


class MarketingChannels(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        filial = self.request.query_params.get('filial')

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        if filial:
            filters['filial'] = filial

        channels = MarketingChannel.objects.all()
        channel_counts = {}

        for channel in channels:
            channel_counts[channel.name] = Lid.objects.filter(
                marketing_channel=channel,
                **filters,
            ).count()

        return Response(channel_counts)


class CheckRoomFillingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filial = request.query_params.get('filial', None)
        room_id = request.query_params.get('room', None)
        lesson_type = request.query_params.get('lesson_type', None)
        start_time = request.query_params.get('start_time', None)
        end_time = request.query_params.get('end_time', None)
        lesson_duration = request.query_params.get('lesson_duration', "90")  # Default 90 min

        if not filial or not start_time or not end_time or not lesson_type:
            return Response({'error': 'Missing required parameters'}, status=400)

        try:
            start_time = datetime.strptime(start_time, "%H:%M").time()
            end_time = datetime.strptime(end_time, "%H:%M").time()
            lesson_duration = int(lesson_duration)
        except ValueError:
            return Response({'error': 'Invalid input format'}, status=400)

        # Get all rooms in the filial if no specific room is given
        if not room_id:
            room_ids = list(Room.objects.filter(filial_id=filial).values_list("id", flat=True))
        else:
            room_ids = [room_id]

        # Map lesson_type to days
        lesson_days_map = {
            "1": ["Dushanba"],
            "0": ["Seshanba"],
            ".": ["Dushanba", "Seshanba"]
        }
        lesson_days = lesson_days_map.get(lesson_type, [])

        # Get lesson days IDs
        lesson_days_ids = Day.objects.filter(name__in=lesson_days).values_list("id", flat=True)

        # Fetch all active lessons within the specified rooms and lesson days
        active_lessons = Group.objects.filter(
            room_number_id__in=room_ids,
            scheduled_day_type__id__in=lesson_days_ids,
            started_at__lt=end_time,
            ended_at__gt=start_time,
            status="ACTIVE"
        ).order_by("started_at").distinct()

        # **Statistics Calculation**
        total_available_time = (datetime.combine(datetime.today(), end_time) -
                                datetime.combine(datetime.today(), start_time)).seconds // 60
        ic(total_available_time)
        total_available_lesson_hours = (total_available_time // lesson_duration)
        ic(total_available_lesson_hours)

        # **Count occupied lesson hours**
        occupied_lesson_hours = sum(
            (lesson.ended_at.hour * 60 + lesson.ended_at.minute) -
            (lesson.started_at.hour * 60 + lesson.started_at.minute)
            for lesson in active_lessons
        ) // lesson_duration

        ic(occupied_lesson_hours)

        free_lesson_hours = total_available_lesson_hours - occupied_lesson_hours
        ic(free_lesson_hours)

        # **Count number of lesson hour pairs**
        lesson_hour_pairs = occupied_lesson_hours // 2
        ic(lesson_hour_pairs,occupied_lesson_hours)

        # **Count unique groups running in this period**
        total_groups = active_lessons.count()
        ic(total_groups)


        rooms = Room.objects.filter(filial_id=self.request.user.filial.first())


        total_students_capacity = sum(
            [room.room_filling * total_available_lesson_hours for room in rooms]
        )

        for room in rooms:
            print(room.room_filling, total_available_lesson_hours)

        # total_students_capacity = sum(
        #     (total_available_lesson_hours) * (i.room_number.room_filling if i.room_number else 0)
        #     for i in active_lessons
        # )

        ic(total_students_capacity)

        # total_students_capacity -= sum(occupied_lesson_hours * room.room_filling for room in rooms)

        ic(total_students_capacity)

        if lesson_type == "1":
            groups_students = StudentGroup.objects.filter(filial_id=filial,
                                                          group__scheduled_day_type__name__in=["Dushanba"])
        elif lesson_type == "0":
            groups_students = StudentGroup.objects.filter(filial_id=filial,
                                                          group__scheduled_day_type__name__in=["Seshanba"])
        else :
            groups_students = StudentGroup.objects.filter(filial_id=filial)


        if lesson_type == "1":
            new_students = StudentGroup.objects.filter(filial_id=filial,student__student_stage_type="NEW_STUDENT",
                                                          group__scheduled_day_type__name__in=["Dushanba"])
        elif lesson_type == "0":
            new_students = StudentGroup.objects.filter(filial_id=filial,student__student_stage_type="NEW_STUDENT",
                                                          group__scheduled_day_type__name__in=["Seshanba"])
        else :
            new_students = StudentGroup.objects.filter(filial_id=filial,student__student_stage_type="NEW_STUDENT",)

        # **Generate final statistics response**
        return Response({
            "groups_students": groups_students.count(),
            "new_students": new_students.count(),
            "total_available_lesson_hours": total_available_lesson_hours,
            "occupied_lesson_hours": occupied_lesson_hours,
            "free_lesson_hours": free_lesson_hours,
            "lesson_hour_pairs": lesson_hour_pairs,
            "total_groups": total_groups,
            "total_students_capacity": (total_students_capacity *( 1 if lesson_type in ["1", "0"] else 3)) - groups_students.count(),
            "all_places":total_students_capacity,
            "weeks_capacity": total_students_capacity *(1 if lesson_type in ["1", "0"] else 3) ,
            "AAAAAAAAAAAA": lesson_type in ["1", "0"]
        })


class DashboardLineGraphAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        from datetime import datetime
        from django.db.models import Sum
        from django.db.models.functions import ExtractWeekDay

        # Extract parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        casher_id = request.query_params.get('cashier')
        filial = request.query_params.get('filial')

        filters = {}

        # Filter by Casher if provided
        if casher_id:
            try:
                casher = Casher.objects.get(id=casher_id)
                filters['casher__id'] = casher.id
            except Casher.DoesNotExist:
                return Response({"error": "Casher not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by start_date and end_date if provided
        if start_date:
            try:
                filters['created_at__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)

        if filial:
            filters['filial__id'] = filial

        if end_date:
            try:
                filters['created_at__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."},
                                status=status.HTTP_400_BAD_REQUEST)

        # Define weekdays mapping
        weekday_map = {
            1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
            5: 'Thursday', 6: 'Friday', 7: 'Saturday'
        }

        # Initialize default structure for all weekdays
        full_week_data = {day: {"income": 0, "expense": 0} for day in weekday_map.values()}

        # Fetch income data
        income_queryset = (
            Finance.objects
            .filter(action="INCOME", **filters)
            .annotate(weekday=ExtractWeekDay('created_at'))
            .values('weekday')
            .annotate(total_amount=Sum('amount'))
        )

        # Fetch expense data
        expense_queryset = (
            Finance.objects
            .filter(action="EXPENSE", **filters)
            .annotate(weekday=ExtractWeekDay('created_at'))
            .values('weekday')
            .annotate(total_amount=Sum('amount'))
        )

        # Aggregate income data
        for item in income_queryset:
            weekday_name = weekday_map[item['weekday']]
            full_week_data[weekday_name]["income"] = item['total_amount']

        # Aggregate expense data
        for item in expense_queryset:
            weekday_name = weekday_map[item['weekday']]
            full_week_data[weekday_name]["expense"] = item['total_amount']

        # Compute total income and expense
        total_income = sum(item["income"] for item in full_week_data.values())
        total_expense = sum(item["expense"] for item in full_week_data.values())

        # Convert dictionary to list format
        result = [
            {
                "weekday": day,
                "income": total["income"],
                "expense": total["expense"]
            }
            for day, total in full_week_data.items()
        ]

        return Response({
            "data": result,
            "total_income": total_income,
            "total_expense": total_expense
        }, status=status.HTTP_200_OK)


class MonitoringView(APIView):
    def get(self, request, *args, **kwargs):
        # Get query parameters
        full_name = request.query_params.get('search', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        subject_id = request.query_params.get('subject', None)
        course_id = request.query_params.get('course', None)
        filial = request.query_params.get('filial', None)

        # Base queryset for teachers
        teachers = CustomUser.objects.filter(role__in=["TEACHER", "ASSISTANT"]).annotate(
            name=Concat(F('first_name'), Value(' '), F('last_name')),
            overall_point=F('monitoring')
        )

        if course_id:
            teachers = teachers.filter(teachers_groups__course__id=course_id)  # ✅ Correct related_name usage

        if subject_id:
            teachers = teachers.filter(teachers_groups__course__subject__id=subject_id)
        if full_name:
            teachers = teachers.filter(name__icontains=full_name)
        if filial:
            teachers = teachers.filter(filial__id=filial)
        if start_date and end_date:
            teachers = teachers.filter(created_at__date__gte=start_date, created_at__lte=end_date)
        elif start_date:
            teachers = teachers.filter(created_at__date__gte=start_date)
        elif end_date:
            teachers = teachers.filter(created_at__date__lte=end_date)

        teacher_data = []

        for teacher in teachers:
            subjects_query = (
                Group.objects.filter(teacher=teacher)
                .annotate(
                    subject_id=F("course__subject__id"),
                    subject_name=F("course__subject__name")
                )
                .values("subject_id", "subject_name")  # Ensure renamed fields are used in values()
            )
            if subject_id:
                subjects_query = subjects_query.filter(id=subject_id)

            subjects = list(subjects_query)

            if start_date and end_date:
                results = Results.objects.filter(teacher=teacher, created_at__gte=start_date
                                                 , created_at_lte=end_date).count()
            elif start_date:
                results = Results.objects.filter(teacher=teacher, created_at__gte=start_date)
            else:
                results = Results.objects.filter(teacher=teacher).count()

            # Use FileUploadSerializer for the photo (handling None cases)
            image_data = FileUploadSerializer(teacher.photo,
                                              context={"request": request}).data if teacher.photo else None

            teacher_data.append({
                "id": teacher.id,
                "full_name": teacher.name,
                "image": image_data,
                "overall_point": teacher.overall_point,
                "subjects": subjects,
                "results": results,
            })

        return Response(teacher_data)


class MonitoringExcelDownloadView(APIView):
    def get(self, request):
        # Create a workbook and get the active worksheet
        wb = Workbook()
        ws = wb.active
        ws.title = "ALL_ASOS"

        # Set column widths
        ws.column_dimensions['A'].width = 25
        for col in ['B', 'D', 'F', 'H', 'J', 'L', 'N', 'P', 'R', 'T', 'V', 'X', 'Z', 'AB', 'AD', 'AF', 'AH']:
            ws.column_dimensions[col].width = 5
        for col in ['C', 'E', 'G', 'I', 'K', 'M', 'O', 'Q', 'S', 'U', 'W', 'Y', 'AA', 'AC', 'AE', 'AG']:
            ws.column_dimensions[col].width = 10

        # Add data to the worksheet
        data = [
            ["ASOSLAR", "", "1", "", "2", "", "3", "4", "5", "6", "", "7", "", "", "", "", "8", "", "", "", "", "", "9",
             "", "", "", "", "", "10", "11", "12", "13", "14", "JAMI"],
            ["", "", "OYLIK HISOBDA", "", "", "", "KIRILGAN DARS", "OYLIK HISOBDA", "OYLIK HISOBDA", "OYLIK HISOBDA",
             "", "OYLIK HISOBDA", "", "", "", "", "TESTGA JALB QILINISHI BO`YICHA H.BALL", "", "", "", "", "",
             "O`RTACHA O`ZLASHTIRISH FOIZI BO`YICHA H.BALL", "", "", "", "", "",
             "TABELLARNI TO`LIQ YURUTISHI BO`YICHA H.BALL", "EDU TIZIM BILAN ISHLASHI BO`YICHA H. BALL",
             "Jadval asosida markaz tadbirlarida faol qatnashish, haftalik va oylik (unit va mock) testlar, olimpiadalarda, Yakshanbalik tadbirlarda qatnashgani  uchun\n15 ball",
             "Jadvaldan tashqari tadbirlar, musobaqalar, bellashuvlar, eventlar tashkil etgani uchun\n15 ball",
             "O'quvchilar yoki ota-onalardan tushgan asosli shikoyatlar har biri -10 ball", ""],
            ["", "", "ISHGA O`Z VAQTIDA KELIB KETISH BO`YICHA HISOBLANGAN BALL", "",
             "DARS O`TISH DAVOMATI\nBO`YICHA HISOBLANGAN BALL", "", "DARS ICHI", "DARS TASHQARISI",
             "O`QUVCHI SONI BO`YICHA H. BALL", "OLIB QOLISH \nBO`YICHA H.BALL", "", "TEST JO`NATISH", "", "", "", "",
             "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],
            ["", "",
             "Ishga har kuni vaqtidan 15 daqiqa oldin kelishi\n\n-Har bir kechikishi  \n-Atpechatka bosmaslik\n-10 ball",
             "", "Dars qoldirmasligi\nto`liq o`tilishi \n\nHar bir qoldirilgan dars \n- 15 ball", "", "DARS\n\n1-ILOVA",
             "DARS\n\n2-ILOVA",
             "30+ =  +2  ball\n50+ =  +4  ball\n70+ =  +6  ball\n80+ =  +8  ball\n90+ = +10 ball\n100+ = +15 ball",
             "80%+ = +5 ball\n100%+ = +10 ball\n\n\n 50% =   -5 ball\n40%  = -10 ball", "",
             "CHORSHANBA KUNIGACHA \nTEST BO`LIMIGA JO`NATISH", "", "", "", "",
             "30% =-15 ball  \n 30%+=-10 ball\n50%+= 0 ball", "", "", "",
             "70%+ = 5 ball\n80%+ = 10 ball\n90%+ = 15 ball", "", "30% = -20 ball\n30%+ = -10 ball\n50%+ =  0 ball", "",
             "", "", "INGLIZ TILI", "70%+ =  5 ball\n80%+ = 10 ball\n90%+ = 20 ball",
             "Haftalik test\nOylik test\nUnit test\nLevel test\nMOCK exam \n\nnatijalari to`liq yozilganligi",
             "EDU tizim bilan yaxshi ishlashi\nBuyurmani vaqtida qubul qilishi\nDavomat va yo`qlamani muntazam vaqtida qilishi",
             "", "", "", ""],
            ["USTOZ", "", "TO`LIQ=", "BALL = +15", "TO`LIQ=", "BALL = +15", "BALL \n= +40", "BALL \n= +1000",
             "BALL \n= +15", "BALL \n= +10", "", "OKTABR\nYAKSHANBA", "", "", "", "BALL \n= +20", "OKTABR\nYAKSHANBA",
             "", "", "", "BALL = +15", "", "SENTABR\nYAKSHANBA", "", "", "", "", "BALL = +20", "", "", "", "", "", ""],
            ["", "", "NECHTA", "BALL = -10", "NECHTA", "BALL = -15", "", "", "", "", "", "6", "13", "20", "27",
             "BALL \n= -5", "6", "13", "20", "27", "", "", "6", "13", "20", "27", "M", "", "BALL = +10", "BALL = +10",
             "BALL = +15", "BALL = +15", "BALL \n= -10", ""],
            ["MAX BALL", "", "0", "15", "0", "15", "40", "", "15", "", "10", "20", "20", "20", "20", "=(O7+N7+M7+L7)/4",
             "15", "15", "15", "15", "=(T7+S7+R7+Q7)/4", "", "20", "20", "20", "20", "", "=(Z7+Y7+X7+W7)/4", "10", "10",
             "15", "15", "0", "=AG7+AF7+AE7+AD7+AC7+AB7+U7+P7+K7+I7+H7+G7+F7+D7"],
            ["1", "DONIYOROV SARVAR USTOZ", "0", "15", "0", "15", "38", "20", "15", "0.8", "5", "", "", "", "", "", "",
             "", "", "", "", "", "", "", "", "", "0.65", "=(Z8+Y8+X8)/3", "10", "10", "10", "30", "0",
             "=AG8+AF8+AE8+AD8+AC8+AB8+V8+P8+K8+I8+H8+G8+F8+D8"],
            ["2", "DJUMAYEVA NORGUL USTOZ", "0", "15", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20", "",
             "0", "10", "0", "", "=(T9+S9+R9)/3", "", "10", "10", "10", "", "=(Z9+Y9+X9)/3", "10", "10", "10", "15",
             "0", "=AG9+AF9+AE9+AD9+AC9+AB9+V9+P9+K9+I9+H9+G9+F9+D9"],
            ["3", "JABBOROV SOHIBJON USTOZ", "0", "15", "0", "15", "38", "", "4", "0.8", "5", "", "", "", "", "20", "",
             "10", "0", "0", "", "=(T10+S10+R10)/3", "", "0", "0", "0", "", "=(Z10+Y10+X10)/3", "10", "10", "10", "15",
             "0", "=AG10+AF10+AE10+AD10+AC10+AB10+V10+P10+K10+I10+H10+G10+F10+D10"],
            ["4", "ASHUROV NODIRBEK USTOZ", "0", "15", "0", "15", "38", "40", "2", "0.8", "5", "", "", "", "", "", "",
             "", "", "", "", "=(T11+S11+R11)/3", "", "", "", "", "0.62", "=(Z11+Y11+X11)/3", "10", "10", "10", "", "0",
             "=AG11+AF11+AE11+AD11+AC11+AB11+V11+P11+K11+I11+H11+G11+F11+D11"],
            ["5", "SHODIJONOV DONIYOR USTOZ", "0", "15", "0", "15", "38", "10", "4", "0.8", "5", "", "", "", "", "20",
             "", "0", "15", "0", "", "=(T12+S12+R12)/3", "", "", "5", "", "", "=(Z12+Y12+X12)/3", "10", "10", "10", "",
             "0", "=AG12+AF12+AE12+AD12+AC12+AB12+V12+P12+K12+I12+H12+G12+F12+D12"],
            ["6", "USMONXO'JAEVA SHOHIDA USTOZ", "0", "15", "0", "15", "38", "", "4", "0.8", "5", "", "", "", "", "20",
             "", "5", "5", "5", "", "=(T13+S13+R13)/3", "", "5", "5", "10", "", "=(Z13+Y13+X13)/3", "10", "10", "10",
             "", "0", "=AG13+AF13+AE13+AD13+AC13+AB13+V13+P13+K13+I13+H13+G13+F13+D13"],
            ["7", "CHORIEV EGAMBERDI USTOZ", "0", "15", "0", "15", "37", "", "2", "0.8", "5", "", "", "", "", "20", "",
             "15", "10", "15", "", "=(T14+S14+R14)/3", "", "-10", "0", "0", "", "=(Z14+Y14+X14)/3", "10", "10", "10",
             "", "0", "=AG14+AF14+AE14+AD14+AC14+AB14+V14+P14+K14+I14+H14+G14+F14+D14"],
            ["8", "AMETOVA ZEBO USTOZ", "0", "15", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20", "", "0",
             "15", "10", "", "=(T15+S15+R15)/3", "", "0", "0", "0", "", "=(Z15+Y15+X15)/3", "10", "10", "10", "", "0",
             "=AG15+AF15+AE15+AD15+AC15+AB15+V15+P15+K15+I15+H15+G15+F15+D15"],
            ["9", "SUNNATOV SARDOR USTOZ", "0", "15", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20", "",
             "10", "10", "0", "", "=(T16+S16+R16)/3", "", "0", "5", "0", "", "=(Z16+Y16+X16)/3", "10", "10", "10", "",
             "0", "=AG16+AF16+AE16+AD16+AC16+AB16+V16+P16+K16+I16+H16+G16+F16+D16"],
            ["10", "YO`LDOSHBOEVA RUHSHONA USTOZ", "0", "15", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20",
             "", "0", "5", "5", "", "=(T17+S17+R17)/3", "", "5", "5", "0", "", "=(Z17+Y17+X17)/3", "10", "10", "10", "",
             "0", "=AG17+AF17+AE17+AD17+AC17+AB17+V17+P17+K17+I17+H17+G17+F17+D17"],
            ["11", "BARATOV AKBAR USTOZ", "0", "15", "0", "15", "35", "", "", "0.8", "5", "", "", "", "", "20", "", "0",
             "15", "15", "", "=(T18+S18+R18)/3", "", "0", "-10", "5", "", "=(Z18+Y18+X18)/3", "10", "10", "10", "", "0",
             "=AG18+AF18+AE18+AD18+AC18+AB18+V18+P18+K18+I18+H18+G18+F18+D18"],
            ["12", "HAMDAMOV HAMROBEK USTOZ", "0", "15", "0", "15", "36", "", "10", "0.8", "5", "", "", "", "", "20",
             "", "0", "0", "0", "", "=(T19+S19+R19)/3", "", "0", "0", "-10", "", "=(Z19+Y19+X19)/3", "10", "10", "10",
             "", "0", "=AG19+AF19+AE19+AD19+AC19+AB19+V19+P19+K19+I19+H19+G19+F19+D19"],
            ["13", "ABDULLAEV BOBURBEK USTOZ", "0", "15", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20", "",
             "5", "0", "0", "", "=(T20+S20+R20)/3", "", "10", "0", "0", "", "=(Z20+Y20+X20)/3", "10", "10", "10", "",
             "0", "=AG20+AF20+AE20+AD20+AC20+AB20+V20+P20+K20+I20+H20+G20+F20+D20"],
            ["14", "ISROILOVA DURDONA USTOZ", "0", "15", "0", "15", "37", "", "2", "0.8", "5", "", "", "", "", "20", "",
             "0", "0", "0", "", "=(T21+S21+R21)/3", "", "0", "0", "5", "", "=(Z21+Y21+X21)/3", "10", "10", "10", "",
             "0", "=AG21+AF21+AE21+AD21+AC21+AB21+V21+P21+K21+I21+H21+G21+F21+D21"],
            ["15", "ASRORBEK USTOZ", "0", "15", "0", "15", "34", "", "", "0.8", "5", "", "", "", "", "20", "", "0", "0",
             "5", "", "=(T22+S22+R22)/3", "", "0", "0", "0", "", "=(Z22+Y22+X22)/3", "10", "10", "10", "", "0",
             "=AG22+AF22+AE22+AD22+AC22+AB22+V22+P22+K22+I22+H22+G22+F22+D22"],
            ["16", "TOSHPO'LATOV FIRDAVS  USTOZ", "0", "15", "0", "15", "36", "", "", "0.8", "5", "", "", "", "", "",
             "", "", "", "", "", "=(T23+S23+R23)/3", "", "", "", "", "0.73", "5", "10", "10", "10", "", "0",
             "=AG23+AF23+AE23+AD23+AC23+AB23+V23+P23+K23+I23+H23+G23+F23+D23"],
            ["17", "MURODOVA RUXSORA", "0", "15", "0", "15", "38", "", "2", "0.8", "5", "", "", "", "", "", "", "", "",
             "", "", "=(T24+S24+R24)/3", "", "", "", "", "", "", "10", "10", "10", "", "0",
             "=AG24+AF24+AE24+AD24+AC24+AB24+V24+P24+K24+I24+H24+G24+F24+D24"],
            ["18", "QO'ZIBOYEVA DILNOZA USTOZ", "0", "15", "0", "15", "36", "", "", "0.8", "5", "", "", "", "", "", "",
             "", "", "", "", "=(T25+S25+R25)/3", "", "", "", "", "0.51", "=(Z25+Y25+X25)/3", "10", "10", "10", "", "0",
             "=AG25+AF25+AE25+AD25+AC25+AB25+V25+P25+K25+I25+H25+G25+F25+D25"],
            ["19", "SHOHIDA USTOZ TURK TILI", "0", "15", "0", "15", "36", "", "", "0.8", "5", "", "", "", "", "", "",
             "", "", "", "", "=(T26+S26+R26)/3", "", "", "", "", "", "=(Z26+Y26+X26)/3", "10", "10", "10", "", "0",
             "=AG26+AF26+AE26+AD26+AC26+AB26+V26+P26+K26+I26+H26+G26+F26+D26"],
            ["20", "ASXADULINA YAZILIYA USTOZ", "0", "15", "0", "15", "35", "", "", "0.8", "5", "", "", "", "", "", "",
             "", "", "", "", "=(T27+S27+R27)/3", "", "", "", "", "0.59", "=(Z27+Y27+X27)/3", "10", "10", "10", "", "0",
             "=AG27+AF27+AE27+AD27+AC27+AB27+V27+P27+K27+I27+H27+G27+F27+D27"],
            ["21", "SHUKUROV ABDURAHIM USTOZ", "1", "-15", "0", "15", "38", "", "2", "0.8", "5", "", "", "", "", "20",
             "", "5", "5", "0", "", "=(T28+S28+R28)/3", "", "0", "0", "-10", "", "=(Z28+Y28+X28)/3", "10", "10", "10",
             "", "0", "=AG28+AF28+AE28+AD28+AC28+AB28+V28+P28+K28+I28+H28+G28+F28+D28"],
            ["22", "BEKMURODOVA GO'ZAL USTOZ", "2", "-30", "0", "15", "37", "", "", "0.8", "5", "", "", "", "", "20",
             "", "15", "15", "15", "", "=(T29+S29+R29)/3", "", "0", "0", "0", "", "=(Z29+Y29+X29)/3", "10", "10", "10",
             "", "0", "=AG29+AF29+AE29+AD29+AC29+AB29+V29+P29+K29+I29+H29+G29+F29+D29"],
            ["23", "XUSHMURODOV BEHRUZBEK USTOZ", "1", "-15", "0", "15", "38", "", "", "0.8", "5", "", "", "", "", "",
             "", "", "", "", "", "=(T30+S30+R30)/3", "", "", "", "", "0.64", "=(Z30+Y30+X30)/3", "10", "10", "10", "15",
             "0", "=AG30+AF30+AE30+AD30+AC30+AB30+V30+P30+K30+I30+H30+G30+F30+D30"],
            [
                "MANITORING VA TEST BO`LIMI 2024-YIL OKTABR OYI UCHUN TO`LIQ MANITORING NATIJALARI HISOBOTI BO`LIB, \nHAR BIR QO`YILGAN BALL ASOSLI VA HOLATGA QARAB BERILGAN.",
                "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
                "", "", "", "", "", ""],
            ["REGISTAN LC SERGELI FILIALI \nMONITORING VA TEST BO`LIMI", "", "", "", "", "", "",
             "MONITORING ISHI HISOBOTI", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "",
             "", "", "", "", ""]
        ]

        for row in data:
            ws.append(row)

        # Apply text wrapping and alignment for multi-line cells
        for row in ws.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')

        # Save workbook to a bytes buffer
        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        # Create response with Excel file
        response = Response(buffer.getvalue())
        response['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response['Content-Disposition'] = f'attachment; filename=monitoring_report.xlsx'

        return response


class DashboardWeeklyFinanceAPIView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Extract query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        casher_id = request.query_params.get('casher')
        action_type = request.query_params.get('action')  # INCOME or EXPENSE
        kind = request.query_params.get('kind')  # Dynamically fetched kinds
        filial = request.query_params.get('filial')

        filters = {}

        # Get all dynamic kinds from DB
        existing_kinds = list(Kind.objects.values_list('name', flat=True))  # Fetch all available kinds dynamically

        if filial:
            filters["filial"] = filial
        if casher_id:
            filters['casher__id'] = casher_id

        # Ensure valid action type (INCOME or EXPENSE)
        if action_type and action_type.upper() in ["INCOME", "EXPENSE"]:
            filters['action__exact'] = action_type.upper()
        elif action_type:
            return Response({"error": "Invalid action. Use 'INCOME' or 'EXPENSE'."}, status=400)

        # Filter by start_date and end_date
        if start_date:
            try:
                filters['created_at__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=400)

        if end_date:
            try:
                filters['created_at__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=400)

        # Ensure kind filtering is valid
        if kind:
            if kind not in existing_kinds:
                return Response({"error": f"Invalid kind. Allowed values: {', '.join(existing_kinds)}"}, status=400)
            filters['kind__name'] = kind  # Ensure kind filtering is correctly applied

        # Query and group by weekday
        queryset = (
            Finance.objects.filter(**filters)
            .annotate(weekday=ExtractWeekDay('created_at'))
            .values('weekday', 'kind__name')
            .annotate(total_amount=Sum('amount'))
        )

        # Map weekday numbers to names
        weekday_map = {
            1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
            5: 'Thursday', 6: 'Friday', 7: 'Saturday'
        }

        # Initialize totals for each weekday and category
        weekly_data = {day: {k: 0 for k in existing_kinds} for day in weekday_map.values()}
        total_overall = {k: 0 for k in existing_kinds}  # Overall total per category

        # Populate data
        for item in queryset:
            weekday_name = weekday_map[item['weekday']]
            category = item['kind__name']
            amount = item['total_amount']
            weekly_data[weekday_name][category] += amount
            total_overall[category] += amount  # Aggregate total for percentage calculation

        # Compute category-wise percentages
        total_sum = sum(total_overall.values())  # Total amount of all categories combined

        if total_sum > 0:
            percentages = {
                category: round((total / total_sum) * 100, 2) for category, total in total_overall.items()
            }
        else:
            percentages = {category: 0 for category in existing_kinds}

        # Convert data to response format
        result = [{"weekday": day, "totals": totals} for day, totals in weekly_data.items()]

        return Response({
            "weekly_data": result,
            "percentages": percentages,
            "available_kinds": existing_kinds  # Returning available kinds for front-end usage
        }, status=200)


class ArchivedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filial = request.query_params.get('filial', None)

        lid = Lid.objects.filter(is_archived=True, lid_stage_type="NEW_LID", is_student=False).count()
        order = Lid.objects.filter(is_archived=True, lid_stage_type="ORDERED_LID", is_student=False).count()
        new_student = Student.objects.filter(student_stage_type="NEW_STUDENT", is_archived=True).count()
        student = Student.objects.filter(student_stage_type="ACTIVE_STUDENT", is_archived=True).count()

        if filial:
            lid = Lid.objects.filter(is_archived=True, lid_stage_type="NEW_LID", is_student=False,filial_id=filial).count()
            order = Lid.objects.filter(is_archived=True, lid_stage_type="ORDERED_LID", is_student=False,filial_id=filial).count()
            new_student = Student.objects.filter(student_stage_type="NEW_STUDENT", is_archived=True,filial_id=filial).count()
            student = Student.objects.filter(student_stage_type="ACTIVE_STUDENT", is_archived=True,filial_id=filial).count()

        return Response({
            "lid": lid,
            "order": order,
            "new_student": new_student,
            "student": student,
        })


class SalesApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        creator = request.query_params.get('creator')
        sale = request.query_params.get('sale')
        student = request.query_params.get('student')
        filial = request.query_params.get('filial')

        filters = {}
        if creator:
            filters['creator_id'] = creator  # Use `_id` for ForeignKeys
        if sale:
            filters['sale_id'] = sale
        if student:
            filters['student_id'] = student
        if filial:
            filters['filial_id'] = filial

        chart_data = []

        total_students = SaleStudent.objects.filter(**filters).count()
        total_voucher_amount = \
        VoucherStudent.objects.filter(**filters).aggregate(total=Sum('voucher__amount'))['total'] or 0
        total_sale_discount = \
        SaleStudent.objects.filter(**filters).aggregate(total=Sum('sale__amount'))['total'] or 0
        total_debt = Student.objects.filter(balance__lt=0, **filters).aggregate(total=Sum('balance'))['total'] or 0

        # FIX: Removed incorrect `balance__status` lookup
        total_income = Student.objects.filter(**filters).aggregate(total=Sum('balance'))['total'] or 0

        chart_data.append({
            "total_students": total_students,
            "total_voucher_amount": total_voucher_amount,
            "total_sales_amount": total_sale_discount,
            "total_debt": total_debt,
            "active_students_balance": total_income,  # Active Students
        })

        return Response({"chart_data": chart_data})


class FinanceStatisticsApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        kind_id = self.request.query_params.get('kind')  # Filter by Kind
        creator = self.request.query_params.get('creator')
        student = self.request.query_params.get('student')
        stuff = self.request.query_params.get('stuff')
        casher = self.request.query_params.get('casher')
        payment_method = self.request.query_params.get('payment_method')
        filial = self.request.query_params.get('filial')

        filters = {}
        if filial:
            filters['filial'] = filial
        if kind_id:
            filters['kind__id'] = kind_id
        if creator:
            filters['creator__id'] = creator
        if student:
            filters['student__id'] = student
        if stuff:
            filters['stuff__id'] = stuff
        if casher:
            filters['casher__id'] = casher
        if payment_method:
            filters['payment_method'] = payment_method

        # ✅ Group by `kind__action` instead of `Finance.action`
        finance_stats = (
            Finance.objects.filter(**filters)
            .values("kind__id", "kind__name", "kind__action")  # Using kind__action
            .annotate(total_amount=Sum("amount"))
            .order_by("kind__name")
        )

        # ✅ Organizing INCOME and EXPENSE based on `kind__action`
        income_stats = []
        expense_stats = []
        for entry in finance_stats:
            stat_entry = {
                "kind_id": entry["kind__id"],
                "kind_name": entry["kind__name"],
                "action": entry["kind__action"],
                "total_amount": entry["total_amount"],
            }
            if entry["kind__action"] == "INCOME":  # ✅ Use `kind__action`
                income_stats.append(stat_entry)
            else:
                expense_stats.append(stat_entry)

        return Response(
            {
                "income": income_stats,
                "expenses": expense_stats,
            }
        )


class StudentLanguage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        filial = self.request.query_params.get('filial')
        if filial:
            student_uz = Student.objects.filter(education_lang="UZB", student_stage_type = "ACTIVE_STUDENT",
                                                is_archived=False,  is_frozen=False).count()
            student_eng = Student.objects.filter(education_lang="ENG", student_stage_type = "ACTIVE_STUDENT",
                                                 is_archived=False,  is_frozen=False).count()
            student_ru = Student.objects.filter(education_lang="RU", student_stage_type = "ACTIVE_STUDENT",
                                                is_archived=False,  is_frozen=False).count()
        else:
            student_uz = Student.objects.filter(education_lang="UZB", student_stage_type = "ACTIVE_STUDENT",
                                                is_archived=False,  is_frozen=False).count()
            student_eng = Student.objects.filter(education_lang="ENG", student_stage_type = "ACTIVE_STUDENT",
                                                 is_archived=False,  is_frozen=False).count()
            student_ru = Student.objects.filter(education_lang="RU", student_stage_type = "ACTIVE_STUDENT",
                                                is_archived=False,  is_frozen=False).count()

        return Response({
            "student_uz": student_uz,
            "student_eng": student_eng,
            "student_ru": student_ru,
        })


class ExportDashboardToExcelAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # ✅ 1. Fetch Sales Data
        creator = request.query_params.get('creator')
        sale = request.query_params.get('sale')
        student = request.query_params.get('student')
        filial = request.query_params.get('filial')

        sales_filters = {}
        if creator:
            sales_filters['creator__id'] = creator
        if sale:
            sales_filters['sale__id'] = sale
        if student:
            sales_filters['student__id'] = student
        if filial:
            sales_filters['filial__id'] = filial

        student_count = SaleStudent.objects.filter(**sales_filters).values('creator').annotate(
            total_students=Count('student', distinct=True)
        )

        voucher_sales = SaleStudent.objects.filter(sale__type="VOUCHER", **sales_filters).values('creator').annotate(
            total_voucher_amount=Sum('sale__amount')
        )

        sale_data = SaleStudent.objects.filter(sale__type="SALE", **sales_filters).values('creator').annotate(
            total_sale_discount=Sum(
                Case(
                    When(
                        student__students_group__group__price_type="monthly",
                        then=F('student__students_group__group__price') * F('sale__amount') / Value(100)
                    ),
                    default=Value(0),
                    output_field=DecimalField()
                )
            )
        )

        total_sales = SaleStudent.objects.filter(**sales_filters).values('creator').annotate(
            total_sales_amount=Sum('sale__amount')
        )

        # ✅ 2. Fetch Finance Statistics Data
        finance_filters = {}
        kind_id = request.query_params.get('kind')
        action = request.query_params.get('action')
        creator = request.query_params.get('creator')
        student = request.query_params.get('student')
        stuff = request.query_params.get('stuff')
        casher = request.query_params.get('casher')
        payment_method = request.query_params.get('payment_method')

        if kind_id:
            finance_filters['kind__id'] = kind_id
        if action:
            finance_filters['action'] = action
        if creator:
            finance_filters['creator__id'] = creator
        if student:
            finance_filters['student__id'] = student
        if stuff:
            finance_filters['stuff__id'] = stuff
        if casher:
            finance_filters['casher__id'] = casher
        if payment_method:
            finance_filters['payment_method'] = payment_method

        finance_stats = Finance.objects.filter(**finance_filters).values('kind__id', 'kind__name', 'action').annotate(
            total_amount=Sum('amount')
        ).order_by('kind__name')

        # ✅ 3. Fetch Weekly Finance Data
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        casher_id = request.query_params.get('casher')
        kind = request.query_params.get('kind')

        weekly_filters = {}
        if casher_id:
            weekly_filters['casher__id'] = casher_id
        if kind:
            weekly_filters['kind__name'] = kind
        if start_date:
            weekly_filters['created_at__gte'] = start_date
        if end_date:
            weekly_filters['created_at__lte'] = end_date

        weekly_finance_data = (
            Finance.objects.filter(**weekly_filters)
            .values('kind__name')
            .annotate(total_amount=Sum('amount'))
        )

        # ✅ Create Excel Workbook
        workbook = Workbook()

        # ✅ Create Sales Sheet
        sales_sheet = workbook.active
        sales_sheet.title = "Sales Data"
        sales_headers = ["Yaratuvchi xodim", "Jami Studentlar", "Voucher Sales", "Sale Discount", "Total Sales"]
        sales_sheet.append(sales_headers)

        for entry in student_count:
            creator_id = entry['creator']
            voucher_entry = next((v for v in voucher_sales if v['creator'] == creator_id), {'total_voucher_amount': 0})
            sale_entry = next((s for s in sale_data if s['creator'] == creator_id), {'total_sale_discount': 0})
            total_sales_entry = next((t for t in total_sales if t['creator'] == creator_id), {'total_sales_amount': 0})

            sales_sheet.append([
                entry['total_students'],
                voucher_entry['total_voucher_amount'],
                sale_entry['total_sale_discount'],
                total_sales_entry['total_sales_amount'],
            ])

        # ✅ Create Finance Statistics Sheet
        finance_sheet = workbook.create_sheet(title="Finance Statistics")
        finance_headers = ["Kind Name", "Action", "Total Amount"]
        finance_sheet.append(finance_headers)

        for entry in finance_stats:
            finance_sheet.append([
                entry['kind__name'],
                entry['action'],
                entry['total_amount']
            ])

        # ✅ Create Weekly Finance Data Sheet
        weekly_sheet = workbook.create_sheet(title="Weekly Finance")
        weekly_headers = ["Kind Name", "Total Amount"]
        weekly_sheet.append(weekly_headers)

        for entry in weekly_finance_data:
            weekly_sheet.append([
                entry['kind__name'],
                entry['total_amount']
            ])

        # ✅ Style headers
        for sheet in [sales_sheet, finance_sheet, weekly_sheet]:
            for col_num, header in enumerate(sheet[1], 1):
                cell = sheet.cell(row=1, column=col_num)
                cell.font = Font(bold=True, size=12)
                cell.alignment = Alignment(horizontal="center", vertical="center")
                sheet.column_dimensions[cell.column_letter].width = 20

        # ✅ Create HTTP Response
        response = HttpResponse(
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        response["Content-Disposition"] = 'attachment; filename="Dashboard_Data.xlsx"'
        workbook.save(response)

        return response


class AdminLineGraph(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        call_operator = request.query_params.get('call_operator')
        lid_type = request.query_params.get('type')

        # Parse date strings into actual date objects
        start_date = parse_date(start_date) if start_date else None
        end_date = parse_date(end_date) if end_date else None

        filial = request.query_params.get('filial')

        # Base filters
        lid_filter = {}
        student_filter = {}
        if filial:
            lid_filter['filial_id'] = filial
            student_filter['filial_id'] = filial

        if start_date:
            lid_filter['created_at__gte'] = start_date
            student_filter['created_at__gte'] = start_date
        if end_date:
            lid_filter['created_at__lte'] = end_date
            student_filter['created_at__lte'] = end_date
        if call_operator:
            lid_filter['call_operator'] = call_operator
        if lid_type:
            lid_filter['type'] = lid_type

        # Query for each type
        lid_new = Lid.objects.filter(lid_stage_type="NEW_LID", **lid_filter)
        lid_ordered = Lid.objects.filter(lid_stage_type="ORDERED_LID", **lid_filter)
        student_new = Student.objects.filter(student_stage_type="NEW_STUDENT", **student_filter)
        student_active = Student.objects.filter(student_stage_type="ACTIVE_STUDENT", **student_filter)

        # Function to process data and fill missing dates
        def get_counts(queryset, date_field="created_at"):
            counts = queryset.values(f"{date_field}__date").annotate(count=Count("id"))
            date_counts = defaultdict(int)

            if start_date and end_date:
                current_date = start_date
                while current_date <= end_date:
                    date_counts[current_date] = 0
                    current_date += timedelta(days=1)

            for entry in counts:
                date_counts[entry[f"{date_field}__date"]] = entry["count"]

            return [{"date": date.strftime("%Y-%m-%d"), "count": count} for date, count in sorted(date_counts.items())]

        # Construct the response
        response_data = {
            "new_lid": (get_counts(lid_new)),
            "ordered_lid": get_counts(lid_ordered),
            "new_student": get_counts(student_new),
            "active_student": get_counts(student_active),
        }

        return Response(response_data)