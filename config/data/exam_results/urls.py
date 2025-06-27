from django.urls import include, path

from data.exam_results.views import QuizRestAPIView, UnitTestListCreateAPIView, UnitTestRetrieveUpdateDestroyAPIView, \
    UnitTestResultListCreateAPIView

urlpatterns = [
    path('', QuizRestAPIView.as_view()),

    path("unit-test/",UnitTestListCreateAPIView.as_view()),
    path("unit-test/<uuid:pk>",UnitTestRetrieveUpdateDestroyAPIView.as_view()),

    path("unit/",UnitTestResultListCreateAPIView.as_view()),

]