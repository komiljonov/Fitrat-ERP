from django.urls import path
from .views import (
    QuizListCreateView,
    QuizRetrieveUpdateDestroyView,
    QuestionListCreateView,
    QuestionRetrieveUpdateDestroyView,
    QuestionCheckAnswerView,
    QuizBulkCheckView, QuizImportView, FillGapsView, FillGapsDetailsView, VocabularyListView, VocabularyDetailsView,
    PairsListView, PairsDetailsView, MatchPairsListView, MatchPairsDetailsView
)

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list'),
    path('<uuid:pk>/', QuizRetrieveUpdateDestroyView.as_view(), name='quiz-detail'),
    path('<uuid:quiz_pk>/questions/', QuestionListCreateView.as_view(), name='question-list'),
    path('<uuid:quiz_pk>/questions/<uuid:pk>/', QuestionRetrieveUpdateDestroyView.as_view(), name='question-detail'),
    path('<uuid:quiz_pk>/questions/<uuid:pk>/check/', QuestionCheckAnswerView.as_view(), name='question-check'),
    path('<uuid:quiz_pk>/check-bulk/', QuizBulkCheckView.as_view(), name='quiz-check-bulk'),

    path('import-quiz/', QuizImportView.as_view(), name='import-quiz'),

    path("fill_gaps/",FillGapsView.as_view(), name='fill-gaps' ),
    path("fill_gaps/<uuid:pk>", FillGapsDetailsView.as_view(), name='fill-gaps'),

    path("vocabularies/", VocabularyListView.as_view(), name='vocabulary-list'),
    path("vocabularies/<uuid:pk>", VocabularyDetailsView.as_view(), name='vocabulary-detail'),

    path("pairs/",PairsListView.as_view(), name='pairs'),
    path("pairs/<uuid:pk>", PairsDetailsView.as_view(), name='pairs-uuid'),

    path("match-pairs/", MatchPairsListView.as_view(), name='match-pairs'),
    path("match-pairs/<uuid:pk>", MatchPairsDetailsView.as_view(), name='match-pairs'),

]