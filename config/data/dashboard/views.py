from rest_framework.response import Response
from rest_framework.views import APIView

from data.department.marketing_channel.models import MarketingChannel
from data.department.marketing_channel.serializers import MarketingChannelSerializer
from data.finances.finance.models import Finance
from data.lid.new_lid.models import Lid
from data.student.groups.models import Room
from data.student.studentgroup.models import StudentGroup


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

        # Query counts for dashboard data with start_date and end_date filters
        orders = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        orders_archived = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        first_lesson = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        first_lesson_archived = Lid.objects.filter(
            is_archived=False,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARSGA_KELMAGAN",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        first_lesson_come = Lid.objects.filter(
            is_archived=True,
            is_frozen=False,
            lid_stage_type="ORDERED_LID",
            ordered_stages="BIRINCHI_DARS_BELGILANGAN",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        first_lesson_come_archived = 35  # Static value, update as needed

        first_course_payment = Finance.objects.filter(
            action="INCOME",
            kind="COURSE_PAYMENT",
            is_first=True,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        first_course_payment_archived = Finance.objects.filter(
            action="INCOME",
            kind="COURSE_PAYMENT",
            is_first=True,
            student__is_archived=True,
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()

        course_ended = StudentGroup.objects.filter(
            group__status="INACTIVE",
            created_at__gte=start_date,
            created_at__lte=end_date,
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

        channels = MarketingChannel.objects.all()
        channel_counts = {}

        for channel in channels:
            channel_counts[channel.name] = Lid.objects.filter(
                marketing_channel=channel,
                created_at__gte=start_date,
                created_at__lte=end_date,
            ).count()

        return Response(channel_counts)

class Room_place(APIView):
    def get(self, request, *args, **kwargs):
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        rooms = Room.objects.all()
        all_places = 0
        for room in rooms:
            all_places += room.room_filling

        is_used = StudentGroup.objects.filter(
            group__status="ACTIVE",
            created_at__gte=start_date,
            created_at__lte=end_date,
        ).count()
        is_free = all_places - is_used

        response = {
            "all_places": all_places,
            "is_used": is_used,
            "is_free": is_free,
        }
        return Response(response)
