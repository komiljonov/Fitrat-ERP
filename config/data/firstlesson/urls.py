from django.urls import path

from .views import (
    FirstLessonListCreateAPIView,
    FirstLessonRetrieveAPIView,
    FirstLessonAttendanceListAPIView,
    FirstLessonLeadNoPgAPIView,
)


urlpatterns = [
    path("", FirstLessonListCreateAPIView.as_view()),
    path("leads/no-pg", FirstLessonLeadNoPgAPIView.as_view()),
    path("<uuid:pk>", FirstLessonRetrieveAPIView.as_view()),
    path("<uuid:pk>/attendances", FirstLessonAttendanceListAPIView.as_view()),
]
