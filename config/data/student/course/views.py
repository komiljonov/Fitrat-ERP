from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

# Create your views here.

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Course
from .serializers import CourseSerializer

class CourseList(ListCreateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    # permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    # Use valid fields that exist in the Course model
    search_fields = ('name', 'subject__name')  # Ensure these are text-based fields (e.g., CharField)
    ordering_fields = ('status',)  # Ensure 'status' exists in the model and supports ordering
    filterset_fields = ('name', 'subject__name')

class CourseDetail(RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


class CourseNoPG(ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
