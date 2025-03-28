from django.urls import include, path

from data.student.homeworks.views import HomeworkListCreateView, HomeworkDetailView

urlpatterns = [
    path("",HomeworkListCreateView.as_view()),
    path("<uuid:pk>/",HomeworkDetailView.as_view()),
]