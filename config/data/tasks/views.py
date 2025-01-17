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
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ("creator", "performer","task","comment","date_of_expired","status")
    ordering_fields = ("date_of_expired",)
    filterset_fields = ("status",)

    def get_queryset(self):
        queryset = Task.objects.filter(creator=self.request.user).order_by("-date_of_expired")
        return queryset


class TaskRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

class TaskListNoPGView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class TaskLidRetrieveListAPIView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self,**kwargs):
        lid = Lid.objects.get(id=kwargs.get('pk'))
        if lid:
            return Task.objects.filter(lid__id=lid).first()

class TaskStudentRetrieveListAPIView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self,**kwargs):
        student = Student.objects.get(id=kwargs.get('pk'))
        if student:
            return Task.objects.filter(student__id=student).first()

