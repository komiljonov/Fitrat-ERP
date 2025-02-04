from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subject, Level, Theme
# Create your views here.
from .serializers import SubjectSerializer, LevelSerializer, ThemeSerializer
from ..groups.models import Group


class SubjectList(ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectDetail(RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectNoPG(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class LevelList(ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class LevelDetail(RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

class LevelNoPG(ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class ThemeList(ListCreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('title','theme','type',)
    ordering_fields = ('title','theme','type',)
    filterser_fields = ('title','theme','type',)

    def get_queryset(self):
        queryset = Theme.objects.all()

        theme = self.request.query_params.get('theme')
        if theme:
            queryset = queryset.filter(theme=theme)

        id = self.request.query_params.get('id')
        if id:
            try:
                course = Group.objects.get(id=id)  # Agar id yo'q bo'lsa, xatolik qaytaradi
                queryset = queryset.filter(course=course.course)
            except Group.DoesNotExist:
                pass  # Agar Group topilmasa, filtr qo'llanilmaydi

        return queryset


class ThemeDetail(RetrieveUpdateDestroyAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]


class ThemeNoPG(ListAPIView):
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Theme.objects.all()

        # Filter by theme if 'theme' query param is provided
        theme = self.request.query_params.get('theme')
        if theme:
            queryset = queryset.filter(theme=theme)  # Assuming `theme` field is in the `Theme` model

        # Filter by Group ID if 'id' query param is provided
        group_id = self.request.query_params.get('id')
        if group_id:
            try:
                # Retrieve the Group by ID and filter the related Course
                group = Group.objects.get(id=group_id)
                queryset = queryset.filter(course=group.course)  # Assuming Group has a `course` field
            except Group.DoesNotExist:
                return Response({"detail": "Group not found."}, status=404)  # Custom response for invalid Group ID

        return queryset

    def get_paginated_response(self, data):
        return Response(data)
