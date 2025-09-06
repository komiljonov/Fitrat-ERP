from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter

from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    get_object_or_404,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Lesson, FirstLLesson, ExtraLesson, ExtraLessonGroup
from .serializers import (
    LessonSerializer,
    LessonScheduleSerializer,
    FirstLessonSerializer,
    ExtraLessonSerializer,
    ExtraLessonGroupSerializer,
    CombinedExtraLessonSerializer,
)
from data.student.studentgroup.models import StudentGroup
from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LidSerializer


class LessonList(ListCreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)

    search_fields = (
        "name",
        "type",
        "group__name",
        "comment",
        "lesson_status",
    )
    ordering_fields = (
        "name",
        "type",
        "group__name",
        "comment",
        "lesson_status",
    )
    filterset_fields = (
        "name",
        "type",
        "group__name",
        "comment",
        "lesson_status",
    )


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
            return Response(
                {"message": "Lesson created successfully.", "lesson_id": lesson.id}
            )
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

        data = request.data.copy()

        lead_id = data.get("lid") or data.get("lid_id") or data.get("id")
        if not lead_id:
            return Response(
                {"detail": "lid is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        lesson_serializer = FirstLessonSerializer(
            data=data,
            context=self.get_serializer_context(),
        )

        lesson_serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            lead = get_object_or_404(Lid.objects.select_for_update(), pk=lead_id)

            lead_serializer = LidSerializer(
                instance=lead,
                data=data,
                partial=True,
                context={"request": request},
            )

            lead_serializer.is_valid(raise_exception=True)

            lead: "Lid" = lead_serializer.save()

            if lead.first_lesson_created_at is None:
                lead.first_lesson_created_at = timezone.now()
                lead.save()

            group = lesson_serializer.validated_data.get("group")

            if group:

                if StudentGroup.objects.filter(group=group, lid=lead).exists():
                    return Response(
                        {"error": "This lead is already assigned to this group."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                if StudentGroup.objects.filter(
                    group=group,
                    student__phone=lead.phone_number,
                ).exists():
                    return Response(
                        {"error": "This Student is already assigned to this group."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            lesson = lesson_serializer.save(lid=lead)

            # Use the same context for representation
            return Response(
                FirstLessonSerializer(
                    lesson,
                    context=self.get_serializer_context(),
                ).data,
                status=status.HTTP_201_CREATED,
            )


class FirstLessonView(ListAPIView):

    serializer_class = FirstLessonSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.kwargs.get("pk")
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
        """Fetch both ExtraLesson and ExtraLessonGroup, then sort them by started_at."""
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
            key=lambda lesson: (lesson.started_at, lesson.date),
        )
        return combined_lessons

    def list(self, request, *args, **kwargs):
        """Override list to return serialized sorted data"""
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
