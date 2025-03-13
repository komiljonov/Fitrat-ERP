from datetime import datetime
from io import BytesIO

import pandas as pd
from django.db.models import Case, When
from django.db.models import Count, Q
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import ExtractWeekDay, Concat
from django.http import HttpResponse
from icecream import ic
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance, Casher, Kind, SaleStudent
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room, Group
from data.student.studentgroup.models import StudentGroup
from ..account.models import CustomUser
from ..results.models import Results
from ..student.attendance.models import Attendance
from ..student.student.models import Student
from ..upload.serializers import FileUploadSerializer

class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
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

        filters = {}
        if start_date:
            filters["created_at__gte"] = start_date
        if end_date:
            filters["created_at__lte"] = end_date
        if filial:
            filters["filial"] = filial

        lid = Lid.objects.filter(lid_stage_type="NEW_LID", **filters)
        orders = Lid.objects.filter(lid_stage_type="ORDERED_LID", **filters)
        orders_archived = orders
        first_lesson = orders.filter(ordered_stages="BIRINCHI_DARS_BELGILANGAN")

        students_with_one_attendance = Attendance.objects.values("student").annotate(count=Count("id")).filter(
            count=1, **filters).values_list("student", flat=True)

        first_lesson_come = Student.objects.filter(id__in=students_with_one_attendance, **filters)
        first_lesson_come_archived = first_lesson_come

        payment_students = Finance.objects.filter(
            student__isnull=False, kind__name="COURSE_PAYMENT", **filters
        ).values_list("student", flat=True)

        first_course_payment = Student.objects.filter(id__in=payment_students, **filters)
        first_course_payment_archived = first_course_payment

        active_student = StudentGroup.objects.filter(group__status="ACTIVE", **filters)
        course_ended = StudentGroup.objects.filter(group__status="INACTIVE", **filters)

        # Apply additional filters
        if channel_id:
            channel = MarketingChannel.objects.get(id=channel_id)
            lid = lid.filter(marketing_channel=channel)
            orders = orders.filter(marketing_channel=channel)
            orders_archived = orders_archived.filter(marketing_channel=channel)
            first_lesson = first_lesson.filter(marketing_channel=channel)
            first_lesson_come = first_lesson_come.filter(marketing_channel=channel)
            first_lesson_come_archived = first_lesson_come_archived.filter(marketing_channel=channel)
            first_course_payment = first_course_payment.filter(marketing_channel=channel)
            first_course_payment_archived = first_course_payment_archived.filter(marketing_channel=channel)
            active_student = active_student.filter(student__marketing_channel=channel)
            course_ended = course_ended.filter(student__marketing_channel=channel)

        if service_manager:
            lid = lid.filter(service_manager__id=service_manager)
            orders = orders.filter(service_manager__id=service_manager)
            orders_archived = orders_archived.filter(service_manager__id=service_manager)
            first_lesson = first_lesson.filter(service_manager__id=service_manager)
            first_lesson_come = first_lesson_come.filter(service_manager__id=service_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(service_manager__id=service_manager)
            first_course_payment = first_course_payment.filter(service_manager__id=service_manager)
            first_course_payment_archived = first_course_payment_archived.filter(service_manager__id=service_manager)
            active_student = active_student.filter(student__service_manager__id=service_manager)
            course_ended = course_ended.filter(student__service_manager__id=service_manager)

        if sales_manager:
            lid = lid.filter(sales_manager__id=sales_manager)
            orders = orders.filter(sales_manager__id=sales_manager)
            orders_archived = orders_archived.filter(sales_manager__id=sales_manager)
            first_lesson = first_lesson.filter(sales_manager__id=sales_manager)
            first_lesson_come = first_lesson_come.filter(sales_manager__id=sales_manager)
            first_lesson_come_archived = first_lesson_come_archived.filter(sales_manager__id=sales_manager)
            first_course_payment = first_course_payment.filter(sales_manager__id=sales_manager)
            first_course_payment_archived = first_course_payment_archived.filter(sales_manager__id=sales_manager)
            active_student = active_student.filter(student__sales_manager__id=sales_manager)
            course_ended = course_ended.filter(student__sales_manager__id=sales_manager)

        if call_operator:
            lid = lid.filter(call_operator__id=call_operator)
            orders = orders.filter(call_operator__id=call_operator)
            orders_archived = orders_archived.filter(call_operator__id=call_operator)
            first_lesson = first_lesson.filter(call_operator__id=call_operator)
            first_lesson_come = first_lesson_come.filter(call_operator__id=call_operator)
            first_lesson_come_archived = first_lesson_come_archived.filter(call_operator__id=call_operator)
            first_course_payment = first_course_payment.filter(call_operator__id=call_operator)
            first_course_payment_archived = first_course_payment_archived.filter(call_operator__id=call_operator)
            active_student = active_student.filter(student__call_operator__id=call_operator)
            course_ended = course_ended.filter(student__call_operator__id=call_operator)

        if subjects:
            lid = lid.filter(subjects__id=subjects)
            orders = orders.filter(subjects__id=subjects)
            orders_archived = orders_archived.filter(subjects__id=subjects)
            first_lesson = first_lesson.filter(subjects__id=subjects)
            first_lesson_come = first_lesson_come.filter(subjects__id=subjects)
            first_lesson_come_archived = first_lesson_come_archived.filter(subjects__id=subjects)
            first_course_payment = first_course_payment.filter(subjects__id=subjects)
            first_course_payment_archived = first_course_payment_archived.filter(subjects__id=subjects)
            active_student = active_student.filter(student__subjects__id=subjects)
            course_ended = course_ended.filter(student__subjects__id=subjects)

        if teacher:
            lid = lid.filter(lids_group__group__teacher__id=teacher)
            orders = orders.filter(lids_group__group__teacher__id=teacher)
            orders_archived = orders_archived.filter(lids_group__group__teacher__id=teacher)
            first_lesson = first_lesson.filter(students_group__group__teacher__id=teacher)
            first_lesson_come = first_lesson_come.filter(students_group__group__teacher__id=teacher)
            first_lesson_come_archived = first_lesson_come_archived.filter(students_group__group__teacher__id=teacher)
            first_course_payment = first_course_payment.filter(students_group__group__teacher__id=teacher)
            first_course_payment_archived = first_course_payment_archived.filter(students_group__group__teacher__id=teacher)
            active_student = active_student.filter(group__teacher__id=teacher)
            course_ended = course_ended.filter(group__teacher__id=teacher)

        data = {
            "lids": lid.count(),
            "orders": orders.count(),
            "orders_archived": orders_archived.count(),
            "first_lesson": first_lesson.count(),
            "first_lesson_come": first_lesson_come.count(),
            "first_lesson_come_archived": first_lesson_come_archived.count(),
            "first_course_payment": first_course_payment.count(),
            "active_student": active_student.count(),
            "first_course_payment_archived": first_course_payment_archived.count(),
            "course_ended": course_ended.count(),
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


class Room_place(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        filial = self.request.query_params.get('filial')
        lesson_hours = self.request.query_params.get('lesson_hours')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')


        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        if filial:
            filters['filial'] = filial


        rooms = Room.objects.filter(**filters)
        all_places = 0
        for room in rooms:
            all_places += room.room_filling

        is_used = StudentGroup.objects.filter(
            group__status="ACTIVE",
            **filters,
        ).count()
        is_free = all_places - is_used

        is_used_percent = all_places / 100 * is_used
        is_free_percent = 100 - is_used_percent

        response = {
            "all_places": all_places,
            "is_used": is_used,
            "is_free": is_free,
            "is_used_percent": is_used_percent,
            "is_free_percent": is_free_percent,
        }
        return Response(response)


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
            overall_point=F('ball')
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
    def get(self, request, *args, **kwargs):
        # Get query parameters
        full_name = request.query_params.get('search', None)
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        subject_id = request.query_params.get('subject', None)
        filial = request.query_params.get('filial', None)

        # Base queryset for teachers
        teachers = CustomUser.objects.filter(role__in=["TEACHER", "ASSISTANT"]).annotate(
            name=Concat(F('first_name'), Value(' '), F('last_name')),
            overall_point=F('ball')
        )

        if filial:
            teachers = teachers.filter(filial=filial)
        if full_name:
            teachers = teachers.filter(name__icontains=full_name)

        if start_date and end_date:
            teachers = teachers.filter(created_at__date__range=[start_date, end_date])
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
                results = Results.objects.filter(teacher=teacher, created_at__gte=start_date,
                                                 created_at__lte=end_date).count()
            elif start_date:
                results = Results.objects.filter(teacher=teacher, created_at__gte=start_date).count()
            else:
                results = Results.objects.filter(teacher=teacher).count()

            # Format subjects as a string for Excel
            subject_names = ", ".join([subject["name"] for subject in subjects])

            teacher_data.append({
                "O'qituvchi F.I.O": teacher.full_name,
                "Overall Point": teacher.overall_point,
                "Subjects": subject_names,
                "Results": results,
            })

        # Convert data to a DataFrame
        df = pd.DataFrame(teacher_data)

        # Create an in-memory Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Teachers")

        # Prepare response
        output.seek(0)
        response = HttpResponse(output.read(),
                                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = 'attachment; filename="monitoring_data.xlsx"'

        return response


class DashboardWeeklyFinanceAPIView(APIView):
    permission_classes = [IsAuthenticated]

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

        return Response({
            "lid": lid,
            "order": order,
            "new_student": new_student,
            "student": student,
        })


class SalesApiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        creator = self.request.query_params.get('creator')
        sale = self.request.query_params.get('sale')
        student = self.request.query_params.get('student')
        filial = self.request.query_params.get('filial')

        filters = {}
        if creator:
            filters['creator__id'] = creator
        if sale:
            filters['sale__id'] = sale
        if student:
            filters['student__id'] = student

        # Count total students per creator
        student_count = SaleStudent.objects.filter(**filters).values('creator').annotate(
            total_students=Count('student', distinct=True)
        )

        # Sum up VOUCHER sales
        voucher_sales = SaleStudent.objects.filter(sale__type="VOUCHER", **filters).values('creator').annotate(
            total_voucher_amount=Sum('sale__amount')
        )

        # Calculate SALES with monthly group pricing discount
        sale_data = SaleStudent.objects.filter(sale__type="SALE", **filters).values('creator').annotate(
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

        # Sum of all sales (regardless of type)
        total_sales = SaleStudent.objects.filter(**filters).values('creator').annotate(
            total_sales_amount=Sum('sale__amount')
        )

        total_income = \
            Student.objects.filter(is_archived=False, student_stage_type="ACTIVE_STUDENT",
                                   balance__gt=0).aggregate(total_income=Sum('balance'))['total_income'] or 0
        student_total_debt = \
            Student.objects.filter(is_archived=False, student_stage_type="ACTIVE_STUDENT",
                                   balance__lt=0).aggregate(
                total_debt=Sum('balance'))['total_debt'] or 0

        # Combine data
        chart_data = []
        for entry in student_count:
            creator_id = entry['creator']
            voucher_entry = next((v for v in voucher_sales if v['creator'] == creator_id), {'total_voucher_amount': 0})
            sale_entry = next((s for s in sale_data if s['creator'] == creator_id), {'total_sale_discount': 0})
            total_sales_entry = next((t for t in total_sales if t['creator'] == creator_id), {'total_sales_amount': 0})

            chart_data.append({
                "total_students": entry['total_students'],
                "total_voucher_amount": voucher_entry['total_voucher_amount'],
                "total_sale_discount": sale_entry['total_sale_discount'],
                "total_sales_amount": total_sales_entry['total_sales_amount'],
                "total_debt": student_total_debt,  # Qarzdorlar
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
            student_uz = Student.objects.filter(language_choice="UZB",
                                                is_archived=False, is_frozen=False).count()
            student_eng = Student.objects.filter(language_choice="ENG",
                                                 is_archived=False, is_frozen=False).count()
            student_ru = Student.objects.filter(language_choice="RU",
                                                is_archived=False, is_frozen=False).count()
        else:
            student_uz = Student.objects.filter(language_choice="UZB",
                                                is_archived=False, is_frozen=False).count()
            student_eng = Student.objects.filter(language_choice="ENG",
                                                 is_archived=False, is_frozen=False).count()
            student_ru = Student.objects.filter(language_choice="RU",
                                                is_archived=False, is_frozen=False).count()

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
