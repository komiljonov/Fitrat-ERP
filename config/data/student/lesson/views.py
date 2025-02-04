from django.db.models import Q
from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter,OrderingFilter

from rest_framework.generics import ListAPIView,ListCreateAPIView,RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lesson, FirstLLesson
from .serializers import LessonSerializer, LessonScheduleSerializer, FirstLessonSerializer
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

