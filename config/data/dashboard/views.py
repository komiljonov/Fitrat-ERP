from datetime import datetime

import icecream
from django.db.models import Sum, F, Value, Count
from django.db.models.functions import ExtractWeekDay, Concat
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance, Casher, Kind
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room, Group
from data.student.studentgroup.models import StudentGroup
from ..account.models import CustomUser
from ..results.models import Results
from ..student.attendance.models import Attendance
from ..upload.serializers import FileUploadSerializer


class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        channel = self.request.query_params.get('marketing_channel')
        manager = self.request.query_params.get('manager')
        teacher = self.request.query_params.get('teacher')

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date
        # if channel:
        #     filters['channel'] = channel


        orders = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            marketing_channel=channel,
            **filters,
        ).count()

        orders_archived = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            marketing_channel=channel,
            **filters,
        ).count()

        first_lesson = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            marketing_channel=channel,
            **filters,
        ).count()

        first_lesson_archived = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARSGA_KELMAGAN",
            marketing_channel=channel,
            **filters,
        ).count()

        first_lesson_come = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            marketing_channel=channel,
            **filters,
        ).count()

        att_once = Attendance.objects.values('lid').annotate(attendance_count=Count('id')).filter(attendance_count=1)

        # Step 2: Count lids that have exactly one attendance and are archived
        first_lesson_come_archived = Lid.objects.filter(
            id__in=[a['lid'] for a in att_once],  # Get lids that attended once
            is_archived=True,  # Only count archived ones
            marketing_channel=channel,
        ).count()

        course_payment = Kind.objects.filter(name="Course payment").first()
        first_course_payment = Finance.objects.filter(
            action="INCOME",
            kind=course_payment,
            is_first=True,
            student__marketing_channel=channel,
            **filters,
        ).count()

        first_course_payment_archived = Finance.objects.filter(
            action="INCOME",
            kind=course_payment,
            is_first=True,
            student__is_archived=True,
            student__marketing_channel=channel,
            **filters,
        ).count()

        if StudentGroup.student:
            course_ended = StudentGroup.objects.filter(
                group__status="INACTIVE",
                student__marketing_channel=channel,
                **filters,
            ).count()
        else:
            course_ended = StudentGroup.objects.filter(
                group__status="INACTIVE",
                lid__marketing_channel=channel,
                **filters,
            ).count()

        moved_to_filial = 45  # Static value, update as needed
        come_from_filial = 13  # Static value, update as needed

        lids = Lid.objects.filter(
            is_archived=False,
            marketing_channel=channel,
            is_frozen=False,
        )
        data = {
            "lids" : lids,
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

        # Return the response
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
        casher_id = request.query_params.get('casher')
        payment_type = request.query_params.get('kind')

        filters = {}

        # Filter by Casher if provided
        if casher_id:
            try:
                casher = Casher.objects.get(id=casher_id)
                filters['casher__id'] = casher.id
            except Casher.DoesNotExist:
                return Response({"error": "Casher not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure valid payment_type is provided (INCOME or EXPENSE)
        valid_payment_types = ["INCOME", "EXPENSE"]
        if payment_type and payment_type.upper() in valid_payment_types:
            icecream.ic(payment_type)
            filters['action__exact'] = payment_type.upper()
        elif payment_type:  # Invalid value
            return Response({"error": "Invalid payment type. Use 'INCOME' or 'EXPENSE'."}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by start_date and end_date if provided
        if start_date:
            try:
                filters['created_at__gte'] = datetime.strptime(start_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid start_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if end_date:
            try:
                filters['created_at__lte'] = datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return Response({"error": "Invalid end_date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Query the filtered data and group by weekday
        queryset = (
            Finance.objects
            .filter(**filters)
            .annotate(weekday=ExtractWeekDay('created_at'))  # Extract weekday (1=Sunday, 7=Saturday)
            .values('weekday')
            .annotate(total_amount=Sum('amount'))  # Sum amounts per weekday
        )
        summ = queryset.aggregate(Sum('amount'))

        # Initialize default data for all weekdays
        weekday_map = {
            1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
            5: 'Thursday', 6: 'Friday', 7: 'Saturday'
        }
        full_week_data = {day: 0 for day in weekday_map.values()}

        # Update full week data with actual totals
        for item in queryset:
            weekday_name = weekday_map[item['weekday']]
            full_week_data[weekday_name] = item['total_amount']

        # Convert dictionary to list format
        result = [{"weekday": day, "total_amount": total,"total" : summ} for day, total in full_week_data.items()]

        return Response(result, status=status.HTTP_200_OK)


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
                results = Results.objects.filter(teacher=teacher,created_at__gte=start_date
                                                 ,created_at_lte=end_date).count()
            elif start_date:
                results = Results.objects.filter(teacher=teacher,created_at__gte=start_date)
            else:
                results = Results.objects.filter(teacher=teacher).count()

            # Use FileUploadSerializer for the photo (handling None cases)
            image_data = FileUploadSerializer(teacher.photo, context={"request": request}).data if teacher.photo else None

            teacher_data.append({
                "id": teacher.id,
                "full_name": teacher.name,
                "image": image_data,
                "overall_point": teacher.overall_point,
                "subjects": subjects,
                "results": results,
            })

        return Response(teacher_data)



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
