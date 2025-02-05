from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListAPIView)
from rest_framework.permissions import IsAuthenticated

from .models import Attendance
from .serializers import AttendanceSerializer
from ..lesson.models import Lesson
from ..student.models import Student
# from ...account.permission import RoleBasedPermission
from ...lid.new_lid.models import Lid


class AttendanceList(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class AttendanceListView(ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get('pk')

        lid = Lid.objects.filter(id=id).first()
        if lid:
            return Attendance.objects.filter(lid=lid)

        student = Student.objects.filter(id=id).first()
        if student:
            return Attendance.objects.filter(student=student)

        raise NotFound("No attendance records found for the given ID.")

class LessonAttendanceList(ListAPIView):
    serializer_class = AttendanceSerializer
    queryset = Attendance.objects.all()

    def get_queryset(self, *args, **kwargs):
        themes = self.request.query_params.getlist('theme', None)
        if themes:
            query = Q()
            for theme in themes:
                query &= Q(theme__id=theme)
            return Attendance.objects.filter(query)

        id = self.kwargs.get('pk')
        if id:
            # Ensure we return a queryset, not a single object
            return Attendance.objects.filter(theme__course__group__id=id)

        return Attendance.objects.none()