from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from flask import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .models import Archived

from .serializers import ArchivedSerializer
from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView

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

    def get_queryset(self,**kwargs):
        lid_id = kwargs.get('pk')  # Assuming you pass 'lid_id' in the URL
        student_id = kwargs.get('pk')  # Assuming you pass 'student_id' in the URL

        print(kwargs.items())
        if lid_id:  # If lid_id is provided, filter by lid
            return Archived.objects.filter(lid__id=lid_id)
        elif student_id:  # If student_id is provided, filter by student
            return Archived.objects.filter(student__id=student_id)

        return Archived.objects.none()  # Return empty queryset if neither is provided
