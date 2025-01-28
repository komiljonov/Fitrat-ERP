from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import TeacherSerializer

from ...account.models import CustomUser
from ...account.permission import FilialRestrictedQuerySetMixin
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.mastering.models import Mastering


class TeacherList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    # permission_classes = (IsAuthenticated,)

class TeacherDetail(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

class TeachersNoPGList(ListAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)


class TeacherScheduleView(ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter lessons for the logged-in teacher
        return Lesson.objects.filter(group__teacher=self.request.user).order_by("day", "start_time")




# class TeacherStatistics(FilialRestrictedQuerySetMixin,ListAPIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request, *args, **kwargs):
#         # Calculate statistics
#         Average_assimilation =
#
#         statistics = {
#             "new_students_count": new_students_count,
#             "new_students_total_debt": total_debt,
#             "archived_new_students": archived_new_students,
#         }
#
#
#         # Additional ordered statistics (could be pagination or other stats)
#         ordered_statistics = {
#             "student_count": student_count,
#             "total_income": total_income,  # Serialized data
#             "student_total_debt": student_total_debt,
#             "archived_student": archived_student,
#         }
#
#         # Including both statistics and ordered data in the response
#         response_data = {
#             "statistics": statistics,
#             "ordered_statistics": ordered_statistics,
#         }
#
#         return Response(response_data)

