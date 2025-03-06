from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..lid.new_lid.models import Lid
from ..student.student.models import Student
from ..tasks.models import Task
from ..tasks.serializers import TaskSerializer

class TaskListCreateView(ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    # Updated search_fields
    search_fields = ("creator__first_name", "creator__last_name", "task", "comment", "date_of_expired", "status")

    # Ordering and filtering fields
    ordering_fields = ("date_of_expired",)
    filterset_fields = ("status",)

    def get_queryset(self):
        # Filter tasks by the current user as the creator

        filial = self.request.query_params.get("filial")
        queryset = Task.objects.all()
        if filial:
            queryset = queryset.objects.filter(filial__id=filial)

        queryset = queryset.objects.filter(creator=self.request.user).order_by("-date_of_expired")
        return queryset


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class TaskListNoPGView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filial = self.request.query_params.get("filial")
        queryset = Task.objects.all()
        if filial:
            queryset = queryset.objects.filter(filial__id=filial)
        queryset = queryset.objects.filter(creator=self.request.user).order_by("-date_of_expired")
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class TaskStudentRetrieveListAPIView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        student = Student.objects.filter(id=pk).first()
        lid = Lid.objects.filter(id=pk).first()

        if lid:
            return Task.objects.filter(lid=lid)  # Return queryset instead of .first()
        elif student:
            return Task.objects.filter(student=student)  # Return queryset instead of .first()
        return Task.objects.none()  # Re

