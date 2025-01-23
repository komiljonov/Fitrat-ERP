from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer
from ..groups.models import Group
from ..lesson.models import Lesson
from ..lesson.serializers import LessonSerializer
from ..studentgroup.models import StudentGroup
from ...account.permission import FilialRestrictedQuerySetMixin


class StudentListView(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,OrderingFilter,SearchFilter)
    search_fields = ('first_name','last_name','phone_number','filial','marketing_channel','student_stage_type','is_archived','moderator')
    ordering_fields = ('student_stage_type','is_archived','moderator','marketing_channel','filial')
    filterset_fields = ('student_stage_type','is_archived','moderator','marketing_channel','filial')


class StudentDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

class StudentListNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class StudentScheduleView(FilialRestrictedQuerySetMixin,ListAPIView):
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_groups = StudentGroup.objects.filter(student_id=self.kwargs['pk']).values_list('group_id', flat=True)
        return Lesson.objects.filter(group_id__in=student_groups).order_by("day", "start_time")

