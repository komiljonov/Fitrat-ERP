from datetime import datetime

from django.db.models import Sum
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance, Casher
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room
from data.student.studentgroup.models import StudentGroup
from ..finances.finance.serializers import FinanceSerializer


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
                filters['casher__id'] = casher
            except Casher.DoesNotExist:
                return Response({"error": "Casher not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Filter by payment_type if provided
        if payment_type:
            filters['kind'] = payment_type

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

        # Query the filtered data and include the casher field in the values
        queryset = Finance.objects.filter(**filters)

        # Annotate and aggregate data by date
        data = queryset.annotate(
            total_amount=Sum('amount')
        ).order_by('created_at__date')

        # Serialize the data
        serialized_data = FinanceSerializer(data, many=True)

        return Response(serialized_data.data, status=status.HTTP_200_OK)
