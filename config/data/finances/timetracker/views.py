from django.shortcuts import render

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView
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
        queryset = Employee_attendance.objects.all()
        if filial:
            queryset = queryset.filter(filial__id=filial)
        if id:
            queryset = queryset.filter(user__id=id)
        return queryset


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Employee_attendance.objects.all()
    serializer_class = TimeTrackerSerializer
    permission_classes = [IsAuthenticated]


