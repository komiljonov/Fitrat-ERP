from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Student
from .serializers import StudentSerializer


class StudentListView(ListCreateAPIView):
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

class StudentListNoPG(ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)





