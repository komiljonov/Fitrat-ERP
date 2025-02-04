from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subject, Level, Theme
# Create your views here.
from .serializers import SubjectSerializer,LevelSerializer,ThemeSerializer

from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView

from ...account.permission import FilialRestrictedQuerySetMixin


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
        queryset = Theme.objects.all()  # Start with all themes by default

        # Apply filter for 'theme' if provided
        theme = self.request.query_params.get('theme')
        if theme:
            queryset = queryset.filter(theme=theme)

        # Apply filter for 'id' if provided
        id = self.request.query_params.get('id')
        if id:
            queryset = queryset.filter(group__id=id)

        return queryset


class ThemeDetail(RetrieveUpdateDestroyAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

class ThemeNoPG(ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
