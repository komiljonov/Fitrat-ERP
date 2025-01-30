from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import TeacherSerializer
from ...account.models import CustomUser
from ...account.permission import FilialRestrictedQuerySetMixin
from ...notifications.models import Complaint
from ...results.models import Results
from ...student.groups.models import Group
from ...student.groups.serializers import GroupSerializer
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.studentgroup.models import StudentGroup
from ...student.studentgroup.serializers import StudentsGroupSerializer


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
        Average_assimilation = None
        new_students = StudentGroup.objects.filter(
            group__teacher=self.request.user,
            student__student_stage_type="NEW_STUDENT"
        ).count()

        stopped_students = StudentGroup.objects.filter(
            group__teacher=self.request.user,
            student__is_archived=True,
        ).count()

        active_students = StudentGroup.objects.filter(
            group__teacher=self.request.user,
            student__student_stage_type="ACTIVE_STUDENT"
        ).count()
        low_assimilation = None

        complaints = Complaint.objects.filter(user=self.request.user).count()

        results = Results.objects.filter(teacher=self.request.user, is_accepted="Accepted").count()

        statistics = {
            "Average_assimilation": Average_assimilation,
            "new_students": new_students,
            "education_stopped_students": stopped_students,
            "active_students": active_students,
            "low_assimilation": low_assimilation,
            "complaints": complaints,
            "results": results,
        }
        return Response(statistics)


class Teacher_StudentsView(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name")

    def get_queryset(self):
        group = StudentGroup.objects.filter(group__teacher=self.request.user)
        if group:
            return group
        return StudentGroup.objects.none()


class TeachersGroupsView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')
    ordering_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')
    filterser_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name", 'status')

    def get_queryset(self):
        status = self.request.query_params.get("status")
        teacher_id = self.request.user.pk  # Get the teacher ID

        queryset = Group.objects.filter(teacher__id=teacher_id)  # First filter by teacher

        if status:
            queryset = queryset.filter(status=status)  # Apply status filter if present

        ordering = self.request.query_params.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)  # Explicitly apply ordering

        return queryset
