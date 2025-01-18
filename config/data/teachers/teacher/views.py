from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response

from .serializers import TeacherSerializer

from ...account.models import CustomUser

class TeacherList(ListCreateAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

class TeacherDetail(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

class TeachersNoPGList(ListAPIView):
    queryset = CustomUser.objects.filter(role='TEACHER')
    serializer_class = TeacherSerializer
    permission_classes = (IsAuthenticated,)

    def get_paginated_response(self, data):
        return Response(data)