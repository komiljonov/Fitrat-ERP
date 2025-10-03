from django.urls import path

from data.student.student.v2.views import StudentsStatsAPIView


urlpatterns = [
    path("stats/<str:stage>", StudentsStatsAPIView.as_view()),
]
