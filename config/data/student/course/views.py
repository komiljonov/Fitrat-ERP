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
from ..attendance.serializers import AttendanceSerializer
from ..groups.models import Group
from ..studentgroup.models import StudentGroup


class CourseList(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    # Use valid fields that exist in the Course model
    search_fields = ('name', 'subject__name')  # Ensure these are text-based fields (e.g., CharField)
    ordering_fields = ('status',)  # Ensure 'status' exists in the model and supports ordering
    filterset_fields = ('name', 'subject__name')

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
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        course = Course.objects.filter(id=id).first()
        if course:
            return Attendance.objects.filter(theme__course=course)
        return Attendance.objects.none()