from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils.timezone import make_aware
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, SecondaryAttendance
from data.student.student.models import Student

from .secondary_serializers import SecondaryAttendanceSerializer
from .serializers import AttendanceSerializer
from data.lid.new_lid.models import Lid


class AttendanceList(ListCreateAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    # def post(self, request, *args, **kwargs):
    #     print(request.data)
    #     return super().post(request, *args, **kwargs)

    def get_queryset(self):

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        reason = self.request.GET.get("reason")
        student = self.request.GET.get("student")
        group = self.request.GET.get("group")
        filial = self.request.GET.get("filial")
        queryset = Attendance.objects.all()

        if filial:
            queryset = queryset.filter(group__filial_id=filial)

        if start_date and end_date:
            start_date = make_aware(datetime.strptime(start_date, "%Y-%m-%d"))
            end_date = make_aware(
                datetime.combine(
                    datetime.strptime(end_date, "%Y-%m-%d"), datetime.max.time()
                )
            )

            queryset = queryset.filter(
                created_at__gte=start_date, created_at__lte=end_date
            )

        if group:
            queryset = queryset.filter(group_id=group)

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)

        if student:
            queryset = queryset.filter(student_id=student)

        if reason:
            queryset = queryset.filter(reason=reason)

        return queryset.order_by("-date")


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
            return Response(
                {"detail": "Expected a list of items."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated = []

        for item in data:
            if "id" not in item:
                return Response(
                    {"detail": "Missing 'id' for update item."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                instance = Attendance.objects.get(id=item["id"])
                serializer = AttendanceSerializer(instance, data=item, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                updated.append(serializer.data)
            except Attendance.DoesNotExist:
                return Response(
                    {"detail": f"Attendance with id {item['id']} not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response({"updated": updated}, status=status.HTTP_200_OK)


class AttendanceDetail(RetrieveUpdateDestroyAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]


class AttendanceListView(ListAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self, *args, **kwargs):
        id = self.kwargs.get("pk")

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

        from django.utils.timezone import now
        from datetime import timedelta

        themes = self.request.query_params.getlist("theme", None)
        group_id = self.kwargs.get("pk", None)
        day = "today"

        if group_id == "":
            group_id = None

        query = Q()

        if themes:
            theme_query = Q()
            for theme in themes:
                theme_query &= Q(theme__id=theme)
            query &= theme_query

        if group_id:
            query &= Q(group__id=group_id)

        if day == "today":
            today = now().date()
            tomorrow = today + timedelta(days=1)
            query &= Q(created_at__gte=today, created_at__lt=tomorrow)

        return Attendance.objects.filter(query)

    def get_paginated_response(self, data):
        return Response(data)


class LessonSecondaryAttendanceList(ListAPIView):
    serializer_class = SecondaryAttendanceSerializer

    def get_queryset(self, *args, **kwargs):
        themes = self.request.query_params.getlist("theme", None)
        group_id = self.kwargs.get("pk", None)

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


class SecondaryAttendanceBulkUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, *args, **kwargs):
        data = request.data
        if not isinstance(data, list):
            return Response(
                {"error": "Expected a list of attendance objects"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        updated_instances = []

        for item in data:
            attendance_id = item.get("id")
            if not attendance_id:
                continue

            try:
                instance = SecondaryAttendance.objects.get(id=attendance_id)
            except SecondaryAttendance.DoesNotExist:
                continue

            serializer = SecondaryAttendanceSerializer(
                instance, data=item, partial=True, context={"request": request}
            )
            if serializer.is_valid():
                serializer.save()
                updated_instances.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(updated_instances, status=status.HTTP_200_OK)
