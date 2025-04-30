from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, Student, SecondaryAttendance
from .secondary_serializers import SecondaryAttendanceSerializer
from .serializers import AttendanceSerializer
from ...lid.new_lid.models import Lid


class AttendanceList(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class AttendanceBulkList(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class AttendanceBulkUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        data = request.data

        if not isinstance(data, list):
            return Response({"detail": "Expected a list of items."}, status=status.HTTP_400_BAD_REQUEST)

        updated = []

        for item in data:
            if "id" not in item:
                return Response({"detail": "Missing 'id' for update item."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                instance = Attendance.objects.get(id=item["id"])
                serializer = AttendanceSerializer(instance, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated.append(serializer.data)
            except Attendance.DoesNotExist:
                return Response({"detail": f"Attendance with id {item['id']} not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({
            "updated": updated
        }, status=status.HTTP_200_OK)

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

        # If group_id is an empty string, set it to None
        if group_id == "":
            group_id = None

        query = Q()  # Start with an empty query to chain filters

        # If themes are provided, filter by theme IDs
        if themes:
            theme_query = Q()
            for theme in themes:
                theme_query &= Q(theme__id=theme)
            query &= theme_query

        # If group ID is provided and valid, filter by group ID
        if group_id:
            query &= Q(group__id=group_id)

        return Attendance.objects.filter(query)

    def get_paginated_response(self, data):
        return Response(data)

class LessonSecondaryAttendanceList(ListAPIView):
    serializer_class = SecondaryAttendanceSerializer

    def get_queryset(self, *args, **kwargs):
        themes = self.request.query_params.getlist('theme', None)
        group_id = self.kwargs.get('pk', None)

        # If group_id is an empty string, set it to None
        if group_id == "":
            group_id = None

        query = Q()  # Start with an empty query to chain filters

        # If themes are provided, filter by theme IDs
        if themes:
            theme_query = Q()
            for theme in themes:
                theme_query &= Q(theme__id=theme)
            query &= theme_query

        # If group ID is provided and valid, filter by group ID
        if group_id:
            query &= Q(group__id=group_id)

        return SecondaryAttendance.objects.filter(query)

    def get_paginated_response(self, data):
        return Response(data)

class SecondaryAttendanceList(ListCreateAPIView):
    queryset = SecondaryAttendance.objects.all()
    serializer_class = SecondaryAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer(self, *args, **kwargs):
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True
        return super().get_serializer(*args, **kwargs)


class SecondaryAttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = SecondaryAttendance.objects.all()
    serializer_class = SecondaryAttendanceSerializer
    permission_classes = [IsAuthenticated]

