from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Attendance, Student
from .serializers import AttendanceSerializer
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

    def get_queryset(self, *args, **kwargs):
        themes = self.request.query_params.getlist('theme', None)
        group_id = self.kwargs.get('pk', None)

        query = Q()  # Start with an empty query to chain filters

        # If themes are provided, filter by theme IDs
        if themes:
            theme_query = Q()
            for theme in themes:
                theme_query &= Q(theme__id=theme)
            query &= theme_query

        # If group ID is provided, filter by group ID
        if group_id:
            query &= Q(theme__course__group__id=group_id)

        return Attendance.objects.filter(query)

    def get_paginated_response(self, data):
        return Response(data)



