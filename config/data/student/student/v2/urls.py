from django.urls import path

from data.student.student.v2.views import StudentFreezeAPIView, StudentsStatsAPIView


urlpatterns = [
    path("stats/<str:stage>", StudentsStatsAPIView.as_view()),
    path("<uuid:pk>/freeze", StudentFreezeAPIView.as_view())
]
