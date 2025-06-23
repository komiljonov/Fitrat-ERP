from django.urls import include, path

from data.exam_results.views import QuizRestAPIView

urlpatterns = [
    path('', QuizRestAPIView.as_view()),
]