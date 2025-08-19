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
from ...account.admin import CustomUserAdmin
from ...account.models import CustomUser
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


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


    def create(self, request, *args, **kwargs):

        print(request.data)

        lid_id = request.data.get('id')

        lid = Lid.objects.filter(id=lid_id).first()


        ser = LidSerializer(instance=lid, data=request.data,request=request)

        ser.is_valid(raise_exception=True)
        ser.save()


        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        group = serializer.validated_data.get("group")
        lid = serializer.validated_data.get("lid")

        if group and lid:
            if StudentGroup.objects.filter(group=group, lid=lid).exists():
                return Response({"error": "This LID is already assigned to this group."}, status=status.HTTP_400_BAD_REQUEST)

            if StudentGroup.objects.filter(group=group, student__phone=lid.phone_number).exists():
                return Response({"error": "This Student is already assigned to this group."}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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
        teacher = self.request.query_params.get("teacher", None)
        subject = self.request.query_params.get("subject", None)
        group = self.request.query_params.get("group", None)

        # Filter by date if provided
        query = Q()


        if teacher:
            query &= Q(teacher__id=teacher)

        if date_filter:
            query &= Q(date=date_filter)
        if filial:
            query &= Q(filial=filial)

        individual_lessons = ExtraLesson.objects.filter(query)
        group_lessons = ExtraLessonGroup.objects.filter(query)

        if group:
            group_lessons = group_lessons.filter(group__id=group)
        if subject:
            group_lessons = group_lessons.filter(group__course__subject__id=subject)

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
