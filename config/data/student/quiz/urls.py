from django.urls import path
from .views import (
    QuizListCreateView,
    QuizRetrieveUpdateDestroyView,
    QuestionListCreateView,
    QuestionRetrieveUpdateDestroyView,
    QuestionCheckAnswerView,
    QuizBulkCheckView
)

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list'),
    path('<uuid:pk>/', QuizRetrieveUpdateDestroyView.as_view(), name='quiz-detail'),
    path('<uuid:quiz_pk>/questions/', QuestionListCreateView.as_view(), name='question-list'),
    path('<uuid:quiz_pk>/questions/<uuid:pk>/', QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),
    path('<uuid:quiz_pk>/questions/<uuid:pk>/check/', QuestionCheckAnswerView.as_view(), name='question-check'),
    path('<uuid:quiz_pk>/check-bulk/', QuizBulkCheckView.as_view(), name='quiz-check-bulk')
]