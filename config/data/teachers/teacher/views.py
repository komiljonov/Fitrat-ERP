from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import TeacherSerializer
from ...account.models import CustomUser
from ...account.permission import FilialRestrictedQuerySetMixin
from ...notifications.models import Complaint
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.studentgroup.models import StudentGroup


class TeacherList(FilialRestrictedQuerySetMixin, ListCreateAPIView):
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
        return Lesson.objects.filter(group__teacher=self.request.user
                                     ).order_by("day", "start_time")


class TeacherStatistics(FilialRestrictedQuerySetMixin, ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Calculate statistics
        Average_assimilation = ""
        new_students = StudentGroup.objects.filter(
            teacher=self.request.user,
            student__student_stage_type="NEW_STUDENT"
                                                ).count()

        stopped_students = StudentGroup.objects.filter(
            teacher=self.request.user,
            student__is_archived=True,
        ).count()

        active_students = StudentGroup.objects.filter(
            teacher=self.request.user,
            student__student_stage_type="ACTIVE_STUDENT"
        ).count()
        low_assimilation = ""

        complaints = Complaint.objects.filter(user=self.request.user).count()



        statistics = {
            "Average_assimilation": Average_assimilation,
            "new_students": new_students,
            "education_stopped_students": stopped_students,
            "active_students": active_students,
            "low_assimilation": low_assimilation,
            "complaints": complaints,

        }
        return Response(statistics)
