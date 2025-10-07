from django.db.models import Case, When, Value, IntegerField

from django.shortcuts import get_object_or_404
from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from data.firstlesson.filters import FirstLessonsFilter
from data.firstlesson.models import FirstLesson
from data.firstlesson.serializers import (
    FirstLessonListSerializer,
    FirstLessonSingleSerializer,
)
from data.student.attendance.serializers import AttendanceSerializer

from django.db import transaction


# Create your views here.


class FirstLessonListCreateAPIView(ListCreateAPIView):

    queryset = (
        FirstLesson.objects.filter(archived_at=None)
        .exclude(status="CAME")
        .annotate(
            status_order=Case(
                When(status="DIDNTCOME", then=Value(0)),
                When(status="PENDING", then=Value(1)),
                default=Value(2),
                output_field=IntegerField(),
            )
        )
        .order_by("status_order", "-created_at")
    ).select_related(
        "lead",
        "lead__sales_manager",
        "lead__service_manager",
        "lead__filial",
        "lead__photo",
    )

    serializer_class = FirstLessonListSerializer

    filterset_class = FirstLessonsFilter

    @transaction.atomic
    def perform_create(self, serializer):
        instance: FirstLesson = serializer.save(
            creator=self.request.user if self.request.user.is_authenticated else None
        )

        instance.group.students.get_or_create(lid=instance.lead, first_lesson=instance)


class FirstLessonRetrieveAPIView(RetrieveUpdateDestroyAPIView):

    queryset = FirstLesson.objects.all()

    serializer_class = FirstLessonSingleSerializer


class FirstLessonAttendanceListAPIView(ListAPIView):

    serializer_class = AttendanceSerializer

    def get_serializer(self, *args, **kwargs):

        kwargs.setdefault("context", self.get_serializer_context())

        return AttendanceSerializer(
            *args, remove_fields=["lead", "student", "relatives"], **kwargs
        )

    def get_queryset(self):

        first_lesson = get_object_or_404(FirstLesson, pk=self.kwargs["pk"])

        return first_lesson.lead.attendances.all()
