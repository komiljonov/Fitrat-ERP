from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import StudentGroup, SecondaryStudentGroup
from .serializers import StudentsGroupSerializer, SecondaryStudentsGroupSerializer


class StudentsGroupList(ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    search_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')
    filter_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')
    filterset_fields = (
    'group__name', 'student__first_name', 'lid__first_name', 'student__last_name', 'lid__last_name', 'group__status',
    'group__teacher__id')

    def get_queryset(self):
        if self.request.user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=self.request.user.id)
            return queryset
        else:
            queryset = StudentGroup.objects.filter(group__filial=self.request.user.filial)
            return queryset



class StudentGroupDetail(RetrieveUpdateDestroyAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]


class StudentGroupNopg(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
    def get_queryset(self):
        if self.request.user.role == 'TEACHER':
            queryset = StudentGroup.objects.filter(group__teacher__id=self.request.user.id)
            return queryset
        else:
            queryset = StudentGroup.objects.filter(group__filial=self.request.user.filial)
            return queryset


class GroupStudentList(ListAPIView):
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Fetch the students related to a specific group from the URL path parameter.
        """
        group_id = self.kwargs.get('pk')  # Get the 'pk' from the URL
        queryset = StudentGroup.objects.filter(group__id=group_id)  # Filter by the group id
        return queryset

    def get_paginated_response(self, data):
        return Response(data)


class GroupStudentDetail(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentsGroupSerializer

    def get_queryset(self):
        id = self.kwargs.get('pk')
        print(id)

        return StudentGroup.objects.filter(Q(student=id) | Q(lid=id))



class SecondaryStudentList(ListCreateAPIView):
    serializer_class = SecondaryStudentsGroupSerializer
    queryset = SecondaryStudentGroup.objects.all()
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        if self.request.user.role == 'ASSISTANT':
            queryset = StudentGroup.objects.filter(group__teacher__id=self.request.user.id)
            return queryset
        else:
            queryset = StudentGroup.objects.filter(group__filial=self.request.user.filial)
            return queryset



