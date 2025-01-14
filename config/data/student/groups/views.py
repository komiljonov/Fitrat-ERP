
from django_filters.rest_framework import DjangoFilterBackend
from flask import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Group, StudentGroup
from .serializers import GroupSerializer, StudentGroupSerializer


class StudentGroupsView(ListCreateAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupSerializer
    filter_backends = (DjangoFilterBackend,OrderingFilter,SearchFilter)
    search_fields = ('name','scheduled_day_type')
    ordering_fields = ('name','scheduled_day_type','start_date','end_date','price_type')
    filterset_fields = ('name','scheduled_day_type','price_type')


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

class GroupStudentsListView(ListAPIView):
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self,**kwargs):
        queryset = StudentGroup.objects.filter(group__id=self.kwargs['pk'])
        return queryset


class StudentGroupListView(ListCreateAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,OrderingFilter,SearchFilter)
    search_fields = ('student','group',)
    ordering_fields = ('student','group',)
    filterset_fields = ('student','group',)


class StudentGroupDetailView(RetrieveUpdateDestroyAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]

class StudentGroupListNoPG(ListAPIView):
    queryset = StudentGroup.objects.all()
    serializer_class = StudentGroupSerializer
    permission_classes = [IsAuthenticated]


