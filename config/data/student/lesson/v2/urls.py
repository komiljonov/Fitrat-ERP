from django.urls import path

from data.student.lesson.v2.views import FirstLessonListCreateAPIView


urlpatterns = [path("first_lessons", FirstLessonListCreateAPIView.as_view())]
