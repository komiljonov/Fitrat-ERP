from rest_framework.generics import ListCreateAPIView

from data.firstlesson.models import FirstLesson

# Create your views here.


class FirstLessonListCreateAPIView(ListCreateAPIView):

    queryset = FirstLesson.objects.all()
