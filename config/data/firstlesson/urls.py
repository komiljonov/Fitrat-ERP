from django.urls import path

from .views import FirstLessonListCreateAPIView, FirstLessonRetrieveAPIView


urlpatterns = [
    path("", FirstLessonListCreateAPIView.as_view()),
    path("<uuid:pk>", FirstLessonRetrieveAPIView.as_view()),
]
