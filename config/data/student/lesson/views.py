from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lesson, FirstLLesson, ExtraLesson, ExtraLessonGroup
from .serializers import LessonSerializer, LessonScheduleSerializer, FirstLessonSerializer, ExtraLessonSerializer, \
    ExtraLessonGroupSerializer, CombinedExtraLessonSerializer
from ..studentgroup.models import StudentGroup


class LessonList(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,SearchFilter,OrderingFilter)
    search_fields = ('name',"type",'group__name','comment','lesson_status',)
    ordering_fields = ('name',"type",'group__name','comment','lesson_status',)
    filterset_fields = ('name',"type",'group__name','comment','lesson_status',)


class LessonDetail(RetrieveUpdateDestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class LessonNoPG(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]

    def get_paginated_response(self, data):
        return Response(data)


class LessonSchedule(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Lesson.objects.all()
    serializer_class = LessonScheduleSerializer
    def post(self, request):
        serializer = LessonScheduleSerializer(data=request.data)
        if serializer.is_valid():
            lesson = serializer.save()
            return Response({"message": "Lesson created successfully.", "lesson_id": lesson.id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AllLessonsView(ListAPIView):
    queryset = Lesson.objects.all().order_by("day", "start_time")
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]


class FistLessonView(ListCreateAPIView):
    queryset = FirstLLesson.objects.all()
    serializer_class = FirstLessonSerializer
    permission_classes = [IsAuthenticated]


class FirstLessonView(ListAPIView):


    serializer_class = FirstLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get('pk')
        print(id)
        return FirstLLesson.objects.filter(lid__id=id)


class ExtraLessonView(ListCreateAPIView):
    serializer_class = ExtraLessonSerializer
    permission_classes = [IsAuthenticated]
    queryset = ExtraLesson.objects.all()



class ExtraLessonGroupView(ListCreateAPIView):
    serializer_class = ExtraLessonGroupSerializer
    queryset = ExtraLessonGroup.objects.all()
    permission_classes = [IsAuthenticated]


class ExtraLessonScheduleView(ListAPIView):
    serializer_class = CombinedExtraLessonSerializer

    def get_queryset(self):
        """ Fetch both ExtraLesson and ExtraLessonGroup, then sort them by started_at. """
        date_filter = self.request.query_params.get("date", None)
        filial = self.request.query_params.get("filial", None)

        # Filter by date if provided
        query = Q()
        if date_filter:
            query &= Q(date=date_filter)
        if filial:
            query &= Q(filial=filial)

        # Get all lessons
        individual_lessons = ExtraLesson.objects.filter(query)
        group_lessons = ExtraLessonGroup.objects.filter(query)

        # Combine both queries and sort by started_at
        combined_lessons = sorted(
            list(individual_lessons) + list(group_lessons),
            key=lambda lesson: (lesson.started_at, lesson.date)
        )

        return combined_lessons

    def list(self, request, *args, **kwargs):
        """ Override list to return serialized sorted data """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
