from django.urls import path
from .views import (
    QuizListCreateView,
    QuizRetrieveUpdateDestroyView,
    QuestionRetrieveUpdateDestroyView, FillGapsView, FillGapsDetailsView, VocabularyListView, VocabularyDetailsView,
    LeftPairsListView, LeftPairsDetailsView, MatchPairsListView, MatchPairsDetailsView, ExamListView, ExamDetailsView,
    QuizGapsListView, QuizGapsDetailsView, QuestionsListCreateView, AnswerListCreateView,
    AnswerRetrieveUpdateDestroyView
)

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list'),
    path('<uuid:pk>/', QuizRetrieveUpdateDestroyView.as_view(), name='quiz-detail'),

    path("questions/", QuestionsListCreateView.as_view(), name="question-list"),
    path("questions/<uuid:pk>/", QuestionRetrieveUpdateDestroyView.as_view(), name="question-detail"),

    path("answers/", AnswerListCreateView.as_view(), name="exam-list"),
    path("answers/<uuid:pk>/", AnswerRetrieveUpdateDestroyView.as_view(), name="exam-detail"),

    path("quiz-questions/", QuizGapsListView.as_view(), name="quiz-question-list"),
    path("quiz-questions/<uuid:pk>/", QuizGapsDetailsView.as_view(), name="quiz-question-detail"),

    path("fill_gaps/",FillGapsView.as_view(), name='fill-gaps' ),
    path("fill_gaps/<uuid:pk>", FillGapsDetailsView.as_view(), name='fill-gaps'),

    path("vocabularies/", VocabularyListView.as_view(), name='vocabulary-list'),
    path("vocabularies/<uuid:pk>", VocabularyDetailsView.as_view(), name='vocabulary-detail'),

    path("pair/",LeftPairsListView.as_view(), name='pairs'),
    path("pair/<uuid:pk>", LeftPairsDetailsView.as_view(), name='pairs-uuid'),

    path("match-pairs/", MatchPairsListView.as_view(), name='match-pairs'),
    path("match-pairs/<uuid:pk>", MatchPairsDetailsView.as_view(), name='match-pairs'),

    path("exam/",ExamListView.as_view(), name='exam'),
    path("exam/<uuid:pk>", ExamDetailsView.as_view(), name='exam-details'),

]