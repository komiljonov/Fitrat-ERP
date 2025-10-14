from django.urls import path

from data.student.student.v2.views import StudentFrozenActionListCreateAPIView, StudentsStatsAPIView


urlpatterns = [
    path("stats/<str:stage>", StudentsStatsAPIView.as_view()),
    path("<uuid:pk>/freeze", StudentFrozenActionListCreateAPIView.as_view())
]
