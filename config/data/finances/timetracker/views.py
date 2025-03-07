from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Employee_attendance
from ...account.models import CustomUser
from .serializers import TimeTrackerSerializer

class AttendanceList(ListCreateAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get('filial')
        id = self.request.query_params.get('id')
        action = self.request.query_params.get('action')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        queryset = Employee_attendance.objects.all()

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        if action:
            queryset = queryset.filter(action=action)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if id:
            queryset = queryset.filter(user__id=id)
        return queryset


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]
