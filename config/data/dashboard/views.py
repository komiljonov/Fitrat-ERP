from datetime import datetime
from io import BytesIO

import pandas as pd
from django.db.models import Count, Q, Case, When
from django.db.models import Sum, F, DecimalField, Value
from django.db.models.functions import ExtractWeekDay, Concat
from django.http import HttpResponse
from icecream import ic
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


from django.db.models import Count, Q
from rest_framework.response import Response
from rest_framework.views import APIView

class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        channel_id = request.query_params.get('marketing_channel')
        service_manager = request.query_params.get('service_manager')
        sales_manager = request.query_params.get('sales_manager')
        filial = request.query_params.get('filial')

        filters = {}
        if start_date:
            filters["created_at__gte"] = start_date
        if end_date:
            filters["created_at__lte"] = end_date
        if filial:
            filters["filial"] = filial

        # Dynamic Filtering using Q
        dynamic_filter = Q()
        if channel_id:
            dynamic_filter |= Q(marketing_channel__id=channel_id)
        if service_manager:
            dynamic_filter |= Q(service_manager__id=service_manager)
        if sales_manager:
            dynamic_filter |= Q(sales_manager__id=sales_manager)

        # Run queries only if filters are provided
        if dynamic_filter:
            lid = Lid.objects.filter(lid_stage_type="NEW_LID", is_archived=False).filter(dynamic_filter).count()
            ic(lid)

            orders = Lid.objects.filter(dynamic_filter, lid_stage_type="ORDERED_LID", **filters).count()
            orders_archived = Lid.objects.filter(dynamic_filter, lid_stage_type="ORDERED_LID", is_archived=True, **filters).count()
            first_lesson = Lid.objects.filter(dynamic_filter, lid_stage_type="ORDERED_LID", ordered_stages="BIRINCHI_DARS_BELGILANGAN", **filters).count()

            # Get students with exactly one attendance record
            students_with_one_attendance = Attendance.objects.values("student").annotate(count=Count("id")).filter(
                count=1).values_list("student", flat=True)

            first_lesson_come = Student.objects.filter(id__in=students_with_one_attendance, **filters).filter(dynamic_filter).count()
            first_lesson_come_archived = Student.objects.filter(id__in=students_with_one_attendance, is_archived=True, **filters).filter(dynamic_filter).count()

            # Get students who made their first course payment
            payment_students = Finance.objects.filter(
                student__isnull=False,
                kind__name="COURSE_PAYMENT"
            ).values_list("student", flat=True)

            first_course_payment = Student.objects.filter(id__in=payment_students, **filters).filter(dynamic_filter).count()
            first_course_payment_archived = Student.objects.filter(id__in=payment_students, is_archived=True, **filters).filter(dynamic_filter).count()

            # Courses that ended
            course_ended = StudentGroup.objects.filter(group__status="INACTIVE", **filters).count()

        else:
            lid = Lid.objects.filter(lid_stage_type="NEW_LID", is_archived=False).count()

            orders = Lid.objects.filter( lid_stage_type="ORDERED_LID", **filters).count()
            orders_archived = Lid.objects.filter( lid_stage_type="ORDERED_LID", is_archived=True,
                                                 **filters).count()
            first_lesson = Lid.objects.filter( lid_stage_type="ORDERED_LID",
                                              ordered_stages="BIRINCHI_DARS_BELGILANGAN", **filters).count()

            # Get students with exactly one attendance record
            students_with_one_attendance = Attendance.objects.values("student").annotate(count=Count("id")).filter(
                count=1).values_list("student", flat=True)

            first_lesson_come = Student.objects.filter(id__in=students_with_one_attendance, **filters).count()
            first_lesson_come_archived = Student.objects.filter(id__in=students_with_one_attendance, is_archived=True,
                                                                **filters).count()

            # Get students who made their first course payment
            payment_students = Finance.objects.filter(
                student__isnull=False,
                kind__name="COURSE_PAYMENT"
            ).values_list("student", flat=True)

            first_course_payment = Student.objects.filter(id__in=payment_students, **filters).count()
            first_course_payment_archived = Student.objects.filter(id__in=payment_students, is_archived=True,
                                                                   **filters).count()

            # Courses that ended
            course_ended = StudentGroup.objects.filter(group__status="INACTIVE", **filters).count()

        data = {
            "lids": lid,
            "orders": orders,
            "orders_archived": orders_archived,
            "first_lesson": first_lesson,
            "first_lesson_come": first_lesson_come,
            "first_lesson_come_archived": first_lesson_come_archived,
            "first_course_payment": first_course_payment,
            "first_course_payment_archived": first_course_payment_archived,
            "course_ended": course_ended,
        }

        return Response(data)




class MarketingChannels(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date

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

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date

        rooms = Room.objects.all()
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

        # Base queryset for teachers
        teachers = CustomUser.objects.filter(role__in=["TEACHER", "ASSISTANT"]).annotate(
            name=Concat(F('first_name'), Value(' '), F('last_name')),
            overall_point=F('ball')
        )

        # Apply filters based on query parameters
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

        # Base queryset for teachers
        teachers = CustomUser.objects.filter(role__in=["TEACHER", "ASSISTANT"]).annotate(
            name=Concat(F('first_name'), Value(' '), F('last_name')),
            overall_point=F('ball')
        )

        # Apply filters based on query parameters
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
            subject_names = ", ".join([subject["subject_name"] for subject in subjects])

            teacher_data.append({
                "Full Name": teacher.name,
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

        filters = {}

        # Get all dynamic kinds from DB
        existing_kinds = list(Kind.objects.values_list('name', flat=True))  # Fetch all available kinds dynamically

        # Filter by Casher if provided
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
        action = self.request.query_params.get('action')  # INCOME or EXPENSE
        creator = self.request.query_params.get('creator')
        student = self.request.query_params.get('student')
        stuff = self.request.query_params.get('stuff')
        casher = self.request.query_params.get('casher')
        payment_method = self.request.query_params.get('payment_method')

        filters = {}
        if kind_id:
            filters['kind__id'] = kind_id
        if action:
            filters['action'] = action  # Filter by INCOME or EXPENSE
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

        # Group by kind and calculate sum of amounts
        finance_stats = Finance.objects.filter(**filters).values('kind__id', 'kind__name', 'action').annotate(
            total_amount=Sum('amount')
        ).order_by('kind__name')

        # Organizing INCOME and EXPENSE separately
        income_stats = []
        expense_stats = []
        for entry in finance_stats:
            stat_entry = {
                "kind_id": entry['kind__id'],
                "kind_name": entry['kind__name'],
                "total_amount": entry['total_amount'],
            }
            if entry["action"] == "INCOME":
                income_stats.append(stat_entry)
            else:
                expense_stats.append(stat_entry)

        return Response({
            "income": income_stats,
            "expenses": expense_stats
        })


class StudentLanguage(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
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
