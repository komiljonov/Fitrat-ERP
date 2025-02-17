from rest_framework.response import Response
from rest_framework.views import APIView
from data.department.marketing_channel.models import MarketingChannel
from data.finances.finance.models import Finance
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room
from data.student.studentgroup.models import StudentGroup


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
class FinanceDashboard(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        filters = {}
        if start_date:
            filters['created_at__gte'] = start_date
        if end_date:
            filters['created_at__lte'] = end_date

