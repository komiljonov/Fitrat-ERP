from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subject, Level, Theme
# Create your views here.
from .serializers import SubjectSerializer, LevelSerializer, ThemeSerializer
from ..course.models import Course
from ..groups.models import Group


class SubjectList(ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        filial = self.request.query_params.get('filial', None)
        if filial:
            queryset = queryset.filter(filial=filial)
        return queryset


class SubjectDetail(RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectNoPG(ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Subject.objects.all()
        filial = self.request.query_params.get('filial', None)
        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset
    def get_paginated_response(self, data):
        return Response(data)


class LevelList(ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        subject = self.request.query_params.get('subject', None)
        filial = self.request.query_params.get('filial', None)
        course = self.request.query_params.get('course', None)

        queryset = Level.objects.all()

        if course:
            queryset = queryset.filter(courses__id=course)

        if subject:
            queryset = queryset.filter(subject__id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset


class LevelDetail(RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class LevelNoPG(ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        filial = self.request.query_params.get('filial', None)
        subject = self.request.query_params.get('subject', None)

        queryset = Level.objects.all()

        if subject:
            queryset = queryset.filter(subject__id=subject)

        if filial:
            queryset = queryset.filter(filial__id=filial)
        return queryset

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
        level = self.request.query_params.get('level')
        if theme:
            queryset = queryset.filter(theme=theme)
        course = self.request.query_params.get('course')
        if course:
            queryset = queryset.filter(course__id=course)


        id = self.request.query_params.get('id')

        if level:
            queryset = queryset.filter(course__levels_course__id=level)

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
