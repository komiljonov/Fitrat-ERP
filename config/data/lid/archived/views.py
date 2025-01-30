from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from flask import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Archived

from .serializers import ArchivedSerializer
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView

from ...student.student.models import Student


class ArchivedListAPIView(ListCreateAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)

    search_fields = ('reason',)
    filterset_fields = ('reason',)
    ordering_fields = ('reason',)

class ArchivedDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)


class ListArchivedListNOPgAPIView(ListAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)


class StudentArchivedListAPIView(ListAPIView):
    queryset = Archived.objects.all()
    serializer_class = ArchivedSerializer
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        # Get query parameters
        student_id = request.query_params.get('student_id')
        lid_id = request.query_params.get('lid_id')

        # Initialize the filter condition
        filter_condition = Q()

        # If student_id is provided, filter by student
        if student_id:
            filter_condition &= Q(student__id=student_id)

        # If lid_id is provided, filter by lid
        if lid_id:
            filter_condition &= Q(lid__id=lid_id)

        # Get the filtered queryset
        archived_items = Archived.objects.filter(filter_condition)

        # Serialize the data
        serializer = ArchivedSerializer(archived_items, many=True)
        return Response(serializer.data)
