from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Subject, Level, Theme
# Create your views here.
from .serializers import SubjectSerializer,LevelSerializer,ThemeSerializer

from rest_framework.generics import ListCreateAPIView,ListAPIView,RetrieveUpdateDestroyAPIView

from ...account.permission import FilialRestrictedQuerySetMixin


class SubjectList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

class SubjectDetail(RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]


class SubjectNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class LevelList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]


class LevelDetail(RetrieveUpdateDestroyAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

class LevelNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)



class ThemeList(FilialRestrictedQuerySetMixin,ListCreateAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

class ThemeDetail(RetrieveUpdateDestroyAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

class ThemeNoPG(FilialRestrictedQuerySetMixin,ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)
