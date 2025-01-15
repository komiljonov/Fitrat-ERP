
from django_filters.rest_framework import DjangoFilterBackend
from flask import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Group
from .serializers import GroupSerializer


class StudentGroupsView(ListCreateAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend,OrderingFilter,SearchFilter)
    search_fields = ('name','teacher','scheduled_day_type')
    ordering_fields = ('name','teacher','scheduled_day_type','start_date','end_date','price_type')
    filterset_fields = ('name','teacher','scheduled_day_type','price_type')


class StudentRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

class StudentListAPIView(ListAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer

    def get_paginated_response(self, data):
        return Response(data)




