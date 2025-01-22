from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import TeacherSerializer

from ...account.models import CustomUser
from ...student.lesson.models import Lesson
from ...student.lesson.serializers import LessonSerializer


class TeacherList(ListCreateAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

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

