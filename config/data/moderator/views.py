from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import ModeratorSerializer

from .models import Moderator
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


class ModeratorListAPIView(ListCreateAPIView):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('full_name','phone','role')
    ordering_fields = ('full_name','phone','role')
    filterset_fields = ('full_name','phone','role')


class ModeratorDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

class ModeratorListNoPGView(ListAPIView):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

class ModeratorStudentsListAPIView(ListAPIView):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self,**kwargs):
        id = self.kwargs['pk']
        moderator = Moderator.objects.filter(moderator=id)
        if moderator:
            students = Student.objects.filter(moderator=moderator)
            lids = Lid.objects.filter(moderator=moderator)
            return students.union(lids)
        return []

