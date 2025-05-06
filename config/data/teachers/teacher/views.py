from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from icecream import ic
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TeacherSerializer
from ...account.models import CustomUser
from ...account.permission import FilialRestrictedQuerySetMixin
from ...notifications.models import Complaint
from ...results.models import Results
from ...student.groups.models import Group, SecondaryGroup
from ...student.groups.serializers import GroupSerializer, SecondaryGroupSerializer
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer
from ...student.mastering.models import Mastering, MasteringTeachers
from ...student.mastering.serializers import StuffMasteringSerializer, MasteringSerializer
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup
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


class TeacherStatistics(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer

    def get(self, request, *args, **kwargs):
        teacher = request.user
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        filters = {}
        if start_date:
            filters = {"created_at__gte": start_date}
        if end_date:
            filters["created_at__lte"] = end_date

        statistics = {
            "all_students": StudentGroup.objects.filter(group__teacher=teacher, **filters).count(),
            "new_students": StudentGroup.objects.filter(group__teacher=teacher,
                                                        student__student_stage_type="NEW_STUDENT", **filters).count(),
            "education_stopped_students": StudentGroup.objects.filter(group__teacher=teacher,
                                                                      student__is_archived=True, **filters).count(),
            "active_students": StudentGroup.objects.filter(group__teacher=teacher,
                                                           student__student_stage_type="ACTIVE_STUDENT", **filters).count(),
            "complaints": Complaint.objects.filter(user=teacher, **filters).count(),
            "results": Results.objects.filter(teacher=teacher, status="Accepted", **filters).count(),
            "average_assimilation": None,
            "low_assimilation": None,
        }

        return Response(statistics)

class Teacher_StudentsView(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = ("lid__first_name", "lid__last_name", "student__first_name", "student__last_name")

    def get_queryset(self):

        students = self.request.GET.get("status", None)

        group = StudentGroup.objects.filter(group__teacher=self.request.user)

        if students:
            group = group.filter(student__student_stage_type=students)
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
        status = self.request.GET.get("status")
        teacher_id = self.request.user.pk  # Get the teacher ID

        queryset = Group.objects.filter(Q(teacher__id=teacher_id) | Q(secondary_teacher__id=teacher_id))  # First filter by teacher

        if status:
            queryset = queryset.filter(status=status)  # Apply status filter if present

        ordering = self.request.GET.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)  # Explicitly apply ordering

        return queryset


class AsistantTeachersView(ListAPIView):
    serializer_class = SecondaryGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        status = self.request.GET.get("status")
        teacher_id = self.request.user.pk
        queryset = SecondaryGroup.objects.filter(teacher__id=teacher_id)
        if status:
            queryset = queryset.filter(status=status)
        ordering = self.request.GET.get("ordering")
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class AssistantStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        filters = {}
        if start_date:
            filters["created_at__gte"] = start_date

        if end_date:
            filters["created_at__lte"] = end_date

        students = SecondaryStudentGroup.objects.filter(group__teacher=self.request.user,**filters).count()
        average_assimilation = None
        low_assimilation = None
        high_assimilation = None

        statistics = {
            "students": students,
            "average_assimilation": average_assimilation,
            "high_assimilation": high_assimilation,
            "low_assimilation": low_assimilation
        }
        return Response(statistics)


class TeacherMasteringStatisticsView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = MasteringTeachers.objects.all()
    serializer_class = StuffMasteringSerializer

    def get_queryset(self):
        queryset = MasteringTeachers.objects.filter(teacher=self.request.user)
        if queryset:
            return queryset
        return Mastering.objects.none()


class SecondaryGroupStatic(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        base_qs = SecondaryStudentGroup.objects.filter(group__teacher=request.user)

        all_count = base_qs.count()
        first_count = base_qs.filter(lid__isnull=False).count()
        new_student_count = base_qs.filter(student__student_stage_type="NEW_STUDENT").count()
        active_count = base_qs.filter(student__student_stage_type="ACTIVE_STUDENT").count()

        return Response({
            "all": all_count,
            "first": first_count,
            "new_student": new_student_count,
            "active": active_count
        })

class StudentsAvgLearning(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Get all SecondaryStudentGroup for the teacher
        student_groups = SecondaryStudentGroup.objects.filter(
            group__teacher=request.user
        ).select_related("student")

        # Collect student IDs
        student_ids = [sg.student.id for sg in student_groups if sg.student]

        # Prefetch all mastering records for those students
        masterings = Mastering.objects.filter(student__id__in=student_ids).select_related("student")

        # Serialize
        serializer = MasteringSerializer(masterings, many=True)
        return Response(serializer.data)