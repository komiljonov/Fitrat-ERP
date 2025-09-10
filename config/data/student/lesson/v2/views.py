from rest_framework.generics import ListCreateAPIView

from data.student.lesson.models import FirstLLesson
from data.student.lesson.v2.serializers import FirstLessonSerializer


class FirstLessonListCreateAPIView(ListCreateAPIView):

    serializer_class = FirstLessonSerializer
    queryset = FirstLLesson.objects.select_related(
        "group",
        "lid",
        "lid__sales_manager",
        "lid__filial",
    )
