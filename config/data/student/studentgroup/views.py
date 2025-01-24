from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import StudentsGroupSerializer

from .models import StudentGroup
from ...account.permission import FilialRestrictedQuerySetMixin


class StudentsGroupList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('group__name','student__first_name','lead__first_name','student__last_name','lead__last_name')
    filter_fields = ('group__name','student__first_name','lead__first_name','student__last_name','lead__last_name')
    filterset_fields = ('group__name','student__first_name','lead__first_name','student__last_name','lead__last_name')


class StudentGroupDetail(RetrieveUpdateDestroyAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]


class StudentGroupNopg(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class GroupStudentList(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentsGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Fetch the moderator by ID from the URL path parameter.
        """
        id = self.kwargs.get('pk')
        try:
            return StudentGroup.objects.filter(group__id=id)
        except StudentGroup.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound({"detail": "Group not found."})
