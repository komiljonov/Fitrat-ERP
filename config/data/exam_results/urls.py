from django.urls import include, path

from data.exam_results.views import QuizRestAPIView, UnitTestListCreateAPIView, UnitTestRetrieveUpdateDestroyAPIView

urlpatterns = [
    path('', QuizRestAPIView.as_view()),

    path("unit/",UnitTestListCreateAPIView.as_view()),
    path("unit/<uuid:pk>",UnitTestRetrieveUpdateDestroyAPIView.as_view()),
]