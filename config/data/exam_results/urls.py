from django.urls import include, path

from data.exam_results.views import QuizRestAPIView, UnitTestListCreateAPIView, UnitTestRetrieveUpdateDestroyAPIView, \
    UnitTestResultListCreateAPIView, MockExamListCreateAPIView, MockExamRetrieveUpdateDestroyAPIView, \
    MockExamResultListCreateAPIView, MockExamResultRetrieveUpdateDestroyAPIView, StudentsResultsListAPIView

urlpatterns = [
    path('', QuizRestAPIView.as_view()),

    path("unit-test/",UnitTestListCreateAPIView.as_view()),
    path("unit-test/<uuid:pk>",UnitTestRetrieveUpdateDestroyAPIView.as_view()),

    path("unit/",UnitTestResultListCreateAPIView.as_view()),

    path("mock/",MockExamListCreateAPIView.as_view()),
    path("mock/<uuid:pk>",MockExamRetrieveUpdateDestroyAPIView.as_view()),


    path("mock-results/",MockExamResultListCreateAPIView.as_view()),
    path("mock-results/<uuid:pk>",MockExamResultRetrieveUpdateDestroyAPIView.as_view()),

    path("results/",StudentsResultsListAPIView.as_view()),
]