from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from data.firstlesson.models import FirstLesson
from data.firstlesson.serializers import (
    FirstLessonListSerializer,
    FirstLessonSingleSerializer,
)

# Create your views here.


class FirstLessonListCreateAPIView(ListCreateAPIView):

    queryset = FirstLesson.objects.all()

    serializer_class = FirstLessonListSerializer

    def perform_create(self, serializer):
        return serializer.save(
            creator=self.request.user if self.request.user.is_authenticated else None
        )


class FirstLessonRetrieveAPIView(RetrieveUpdateDestroyAPIView):

    queryset = FirstLesson.objects.all()

    serializer_class = FirstLessonSingleSerializer
