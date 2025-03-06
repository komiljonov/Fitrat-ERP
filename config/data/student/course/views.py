import icecream
from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Create your views here.

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer
from ..attendance.models import Attendance
from ..attendance.serializers import AttendanceSerializer, AttendanceTHSerializer
from ..groups.models import Group
from ..studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...account.models import CustomUser


class CourseList(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    # Use valid fields that exist in the Course model
    search_fields = ('name', 'subject__name')  # Ensure these are text-based fields (e.g., CharField)
    ordering_fields = ('status',)  # Ensure 'status' exists in the model and supports ordering
    filterset_fields = ('name', 'subject__name')

    def get_queryset(self):
        level = self.request.query_params.get('level', None)
        filial = self.request.query_params.get('filial', None)
        queryset = Course.objects.all()
        if filial:
            queryset = queryset.objects.filter(filial=filial)
        else:
            queryset = queryset.objects.filter(filial = self.request.user.filial.first())
        if level:
            queryset =  queryset.objects.filter(level__id=level)
        return queryset

class CourseDetail(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class CourseNoPG(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class StudentCourse(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')

        # Get all StudentGroups that match the filter (either by lid or student id)
        groups = StudentGroup.objects.filter(Q(lid__id=id) | Q(student__id=id)).select_related('group')

        courses = set()  # Use a set to avoid duplicates
        for group in groups:
            if group.group and group.group.course:
                courses.add(group.group.course)

        # Convert set to list to ensure compatibility with the paginator
        return list(courses)


class CourseTheme(ListAPIView):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceTHSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        course = Course.objects.filter(id=id).first()
        print(course)
        if course:
            return Attendance.objects.filter(theme__course=course)
        return Attendance.objects.none()


class CourseTeacher(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        teacher_id = self.kwargs.get('pk')
        user = CustomUser.objects.filter(id=teacher_id).first()
        icecream.ic(user)
        if user.role == 'TEACHER':

            student_groups = StudentGroup.objects.filter(group__teacher__id=teacher_id)

            courses = Course.objects.filter(id__in=student_groups.values('group__course__id')).distinct()

            return courses
        elif user.role == 'ASSISTANT':

            student_groups = SecondaryStudentGroup.objects.filter(group__teacher__id=teacher_id)

            courses = Course.objects.filter(id__in=student_groups.values('group__group__course__id')).distinct()

            return courses

        return Course.objects.none()

