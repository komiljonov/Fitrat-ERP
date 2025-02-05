from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.generics import (ListCreateAPIView,
                                     RetrieveUpdateDestroyAPIView,
                                     ListAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, Student  # Import necessary models
from .serializers import AttendanceSerializer
from .serializers import StudentSerializer  # Ensure this serializer exists
from ..studentgroup.models import StudentGroup
# from ...account.permission import RoleBasedPermission
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


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
            query &= theme_query  # Combine the theme filter with the existing query

        # If group ID is provided, filter by group ID
        if group_id:
            query &= Q(theme__course__group__id=group_id)

        # Apply the combined query to the Attendance model
        return Attendance.objects.filter(query)

    def get_paginated_response(self, data):
        return Response(data)




# class FilterAttendanceView(APIView):
#     def get(self, request, *args, **kwargs):
#         # Get parameters
#         themes = request.query_params.getlist('theme', [])
#         group_id = request.query_params.get('id', None)
#         today = timezone.now().date()
#
#         # Debugging
#         print(f"Themes: {themes}")
#         print(f"Group ID: {group_id}")
#         print(f"Date: {today}")
#
#         if not themes:
#             return Response({'detail': 'No themes provided.'}, status=status.HTTP_400_BAD_REQUEST)
#         if not group_id:
#             return Response({'detail': 'No group_id provided.'}, status=status.HTTP_400_BAD_REQUEST)
#
#         try:
#             student_group = StudentGroup.objects.filter(group__id=group_id)
#             print(student_group)
#         except StudentGroup.DoesNotExist:
#             return Response({'detail': 'Group not found.'}, status=status.HTTP_404_NOT_FOUND)
#
#         students_or_lids_with_attendance = []
#
#         for student_or_lid in student_group:
#             if isinstance(student_or_lid, Student):
#                 # Query for attendance using student
#                 query = Q(created_at=today) & Q(theme__id__in=themes) & Q(student=student_or_lid)
#                 attendance = Attendance.objects.filter(query).first()
#
#                 students_or_lids_with_attendance.append({
#                     'student_or_lid': StudentSerializer(student_or_lid).data,
#                     'attendance': attendance.reason if attendance else None
#                 })
#             elif isinstance(student_or_lid, Lid):
#                 # Query for attendance using lid
#                 query = Q(created_at=today) & Q(theme__id__in=themes) & Q(lid=student_or_lid)
#                 attendance = Attendance.objects.filter(query).first()
#
#                 students_or_lids_with_attendance.append({
#                     'student_or_lid': LidSerializer(student_or_lid).data,
#                     'attendance': attendance.reason if attendance else None
#                 })
#
#         # Prepare final response data
#         data = {
#             'students_or_lids_with_attendance': students_or_lids_with_attendance,
#         }
#
#         return Response(data, status=status.HTTP_200_OK)
