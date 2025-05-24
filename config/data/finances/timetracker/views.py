from django.utils.dateparse import parse_datetime
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Employee_attendance, UserTimeLine
from .serializers import TimeTrackerSerializer
from .serializers import UserTimeLineSerializer


class AttendanceList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer


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
            queryset = queryset.filter(employee_id=user_id)

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