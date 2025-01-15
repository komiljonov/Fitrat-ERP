from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from .serializers import ModeratorSerializer, ModeratorStudentSerializer

from ..account.models import CustomUser
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


class ModeratorListAPIView(ListCreateAPIView):
    queryset = CustomUser.objects.filter(role='MODERATOR')
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('full_name','phone','role')
    ordering_fields = ('full_name','phone','role')
    filterset_fields = ('full_name','phone','role')


class ModeratorDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = CustomUser.objects.filter(role='MODERATOR')
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

class ModeratorListNoPGView(ListAPIView):
    queryset = CustomUser.objects.filter(role='MODERATOR')
    serializer_class = ModeratorSerializer
    permission_classes = [IsAuthenticated]

class ModeratorStudentsListAPIView(RetrieveAPIView):
    """
    Retrieves a moderator along with their associated students and lids.
    """
    serializer_class = ModeratorStudentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Fetch the moderator by ID from the URL path parameter.
        """
        id = self.kwargs.get('pk')
        try:
            return CustomUser.objects.get(id=id, role='MODERATOR')
        except CustomUser.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound({"detail": "Moderator not found."})