from django.urls import path

from .views import FirstLessonListCreateAPIView


urlpatterns = [path("", FirstLessonListCreateAPIView.as_view())]
