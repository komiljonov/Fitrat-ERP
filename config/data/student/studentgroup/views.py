from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import StudentGroupSerializer

from .models import StudentGroup
from ...account.permission import FilialRestrictedQuerySetMixin


class StudentGroupList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('group','student','lead')
    filter_fields = ('group','student','lead')
    filterset_fields = ('group','student','lead')


class StudentGroupDetail(RetrieveUpdateDestroyAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]


class StudentGroupNopg(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)