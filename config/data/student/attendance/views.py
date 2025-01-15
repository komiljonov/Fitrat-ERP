from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Attendance
from .serializers import AttendanceSerializer
from ..student.models import Student
from ...lid.new_lid.models import Lid


class AttendanceList(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class StudentAttendanceList(ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self,*args,**kwargs):
        id = self.kwargs['pk']
        student = Student.objects.get(id=id)
        if student:
            return Attendance.objects.filter(student=student)
        return Attendance.objects.none()

class LidAttendanceList(ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self,*args,**kwargs):
        id = self.kwargs['pk']
        lead = Lid.objects.get(id=id)
        if lead:
            return Attendance.objects.filter(lid=lead)
        return Attendance.objects.none()
