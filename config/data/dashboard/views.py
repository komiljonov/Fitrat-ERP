from datetime import datetime

import icecream
from django.db.models import Sum, F, Value
from django.db.models.functions import ExtractWeekDay, Concat
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance, Casher
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room, Group
from data.student.studentgroup.models import StudentGroup
from ..account.models import CustomUser
from ..finances.finance.serializers import FinanceSerializer
from ..results.models import Results
from ..student.course.models import Course


class DashboardView(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date

        orders = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            **filters,
        ).count()

        orders_archived = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            **filters,
        ).count()

        first_lesson = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            **filters,
        ).count()

        first_lesson_archived = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARSGA_KELMAGAN",
            **filters,
        ).count()

        first_lesson_come = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            **filters,
        ).count()

        first_lesson_come_archived = 35  # Static value, update as needed

        first_course_payment = Finance.objects.filter(
            action="INCOME",
            kind="COURSE_PAYMENT",
            is_first=True,
            **filters,
        ).count()

        first_course_payment_archived = Finance.objects.filter(
            action="INCOME",
            kind="COURSE_PAYMENT",
            is_first=True,
            student__is_archived=True,
            **filters,
        ).count()

        course_ended = StudentGroup.objects.filter(
            group__status="INACTIVE",
            **filters,
        ).count()

        moved_to_filial = 45  # Static value, update as needed
        come_from_filial = 13  # Static value, update as needed

        # Prepare the data for the response
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
        result = [{"weekday": day, "total_amount": total} for day, total in full_week_data.items()]

        return Response(result, status=status.HTTP_200_OK)



class MonitoringView(APIView):
    def get(self, request, *args, **kwargs):
        teachers = CustomUser.objects.filter(role__in=["TEACHER", "ASSISTANT"]).annotate(
            name=Concat(F('first_name'), Value(' '), F('last_name')),
            overall_point=F('ball')
        )

        teacher_data = []

        for teacher in teachers:
            subjects = Group.objects.filter(teacher=teacher).values("id", "name")
            results = Results.objects.filter(teacher=teacher).count()
            teacher_data.append({
                "id": teacher.id,
                "full_name": teacher.name,
                "overall_point": teacher.overall_point,
                "subjects": list(subjects),
                "results": results,
            })

        return Response(teacher_data)

