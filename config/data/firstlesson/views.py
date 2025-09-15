from rest_framework.generics import ListCreateAPIView

from data.firstlesson.models import FirstLesson
from data.firstlesson.serializers import FirstLessonSerializer

# Create your views here.


class FirstLessonListCreateAPIView(ListCreateAPIView):

    queryset = FirstLesson.objects.all()

    serializer_class = FirstLessonSerializer

    def perform_create(self, serializer):
        return serializer.save(creator=self.request.user)
