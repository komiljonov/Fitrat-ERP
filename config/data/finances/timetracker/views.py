from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Employee_attendance, CustomUser, UserTimeLine
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer
from .sinx import TimetrackerSinc  # assuming you keep that class in a separate file

class AttendanceList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        tt = TimetrackerSinc()

        user = CustomUser.objects.filter(id=serializer.data['employee']).first()
        if not user:
            return Response({"error": "User not found"}, status=status.HTTP_400_BAD_REQUEST)

        timelines = UserTimeLine.objects.filter(user=user)
        timeline_by_day = {tl.day: tl for tl in timelines}

        def get_day_times(day_name):
            tl = timeline_by_day.get(day_name)
            if tl:
                return {
                    "start": tl.start_time.strftime("%H:%M"),
                    "end": tl.end_time.strftime("%H:%M")
                }
            else:
                return None

        external_data = {
            "name": user.full_name,
            "phone_number": user.phone,
            "filials": [],  # Add real filial info if available
            "salary": user.salary,
            "wt_monday": get_day_times("Monday"),
            "wt_tuesday": get_day_times("Tuesday"),
            "wt_wednesday": get_day_times("Wednesday"),
            "wt_thursday": get_day_times("Thursday"),
            "wt_friday": get_day_times("Friday"),
            "wt_saturday": get_day_times("Saturday"),
            "wt_sunday": get_day_times("Sunday"),
            "lunch_time": None
        }

        external_response = tt.create_data(external_data)

        return Response({
            "local": serializer.data,
            "external": external_response
        }, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        user_id = self.request.query_params.get('id')
        action = self.request.query_params.get('action')
        type = self.request.query_params.get('type')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        queryset = Employee_attendance.objects.all()

        if start_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date))
        if start_date and end_date:
            queryset = queryset.filter(date__gte=parse_datetime(start_date),
                                       date__lte=parse_datetime(end_date))

        if type:
            queryset = queryset.filter(type=type)
        if action:
            queryset = queryset.filter(action=action)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]


class UserTimeLineList(ListCreateAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer

    def get_queryset(self):
        queryset = UserTimeLine.objects.all()

        user = self.request.GET.get('user')
        day = self.request.GET.get('day')
        if user:
            queryset = queryset.filter(user_id=user)

        if day:
            queryset = queryset.filter(day=day)
        return queryset


class UserTimeLineDetail(RetrieveUpdateDestroyAPIView):
    queryset = UserTimeLine.objects.all()
    serializer_class = UserTimeLineSerializer
    permission_classes = [IsAuthenticated]