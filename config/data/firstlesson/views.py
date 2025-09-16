from django.db.models import Case, When, Value, IntegerField

from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.firstlesson.filters import FirstLessonsFilter
from data.firstlesson.models import FirstLesson
from data.firstlesson.serializers import (
    FirstLessonListSerializer,
    FirstLessonSingleSerializer,
)

# Create your views here.


class FirstLessonListCreateAPIView(ListCreateAPIView):

    queryset = (
        FirstLesson.objects.filter(is_archived=False)
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

    def perform_create(self, serializer):
        instance: FirstLesson = serializer.save(
            creator=self.request.user if self.request.user.is_authenticated else None
        )

        instance.group.students.get_or_create(lid=instance.lead, first_lesson=instance)


class FirstLessonRetrieveAPIView(RetrieveUpdateDestroyAPIView):

    queryset = FirstLesson.objects.all()

    serializer_class = FirstLessonSingleSerializer
