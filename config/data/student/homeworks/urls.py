from django.urls import include, path

from data.student.homeworks.views import HomeworkListCreateView, HomeworkDetailView, HomeworkHistoryListCreateView, \
    HomeworkHistoryView, HomeworkListNoPgCreateView

urlpatterns = [
    path("",HomeworkListCreateView.as_view()),
    path("<uuid:pk>/",HomeworkDetailView.as_view()),
    path("no-pg",HomeworkListNoPgCreateView.as_view()),


    path("history/", HomeworkHistoryListCreateView.as_view()),
    path("history/<uuid:pk>",HomeworkHistoryView.as_view()),

]