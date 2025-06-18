from django.urls import path

from .views import (
    QuizListCreateView,
    QuizRetrieveUpdateDestroyView,
    QuestionRetrieveUpdateDestroyView, FillGapsView, FillGapsDetailsView, VocabularyListView, VocabularyDetailsView,
    LeftPairsListView, LeftPairsDetailsView, MatchPairsListView, MatchPairsDetailsView, ExamListView, ExamDetailsView,
    QuizGapsListView, QuizGapsDetailsView, QuestionsListCreateView, AnswerListCreateView,
    AnswerRetrieveUpdateDestroyView, QuizCheckAPIView, ExcelQuizUploadAPIView, ExamRegistrationListCreateAPIView,
    ObjectiveTestView, Cloze_TestView, ImageCloze_TestView, ExamRegisteredStudentAPIView, QuizListPgView,
    True_False_TestView, True_False_TestRetriveView, Cloze_TestUpdate, ExamCertificateAPIView, ExamSubjectListCreate,
    ExamSubjectDetail, ExamOptionCreate, ExamRegistrationNoPgAPIView
)

urlpatterns = [
    path('', QuizListCreateView.as_view(), name='quiz-list'),
    path('<uuid:pk>/', QuizRetrieveUpdateDestroyView.as_view(), name='quiz-detail'),

    path("no-pg/", QuizListPgView.as_view(), name='quiz-list-pg'),

    path("questions/", QuestionsListCreateView.as_view(), name="question-list"),
    path("questions/<uuid:pk>/", QuestionRetrieveUpdateDestroyView.as_view(), name="question-detail"),

    path("answers/", AnswerListCreateView.as_view(), name="exam-list"),
    path("answers/<uuid:pk>/", AnswerRetrieveUpdateDestroyView.as_view(), name="exam-detail"),

    path("quiz-questions/", QuizGapsListView.as_view(), name="quiz-question-list"),
    path("quiz-questions/<uuid:pk>/", QuizGapsDetailsView.as_view(), name="quiz-question-detail"),

    path("fill_gaps/", FillGapsView.as_view(), name='fill-gaps'),
    path("fill_gaps/<uuid:pk>", FillGapsDetailsView.as_view(), name='fill-gaps'),

    path("vocabularies/", VocabularyListView.as_view(), name='vocabulary-list'),
    path("vocabularies/<uuid:pk>", VocabularyDetailsView.as_view(), name='vocabulary-detail'),

    path("pair/", LeftPairsListView.as_view(), name='pairs'),
    path("pair/<uuid:pk>", LeftPairsDetailsView.as_view(), name='pairs-uuid'),

    path("match-pairs/", MatchPairsListView.as_view(), name='match-pairs'),
    path("match-pairs/<uuid:pk>", MatchPairsDetailsView.as_view(), name='match-pairs'),

    path("objective/", ObjectiveTestView.as_view(), name="objective-test"),
    path("cloze/", Cloze_TestView.as_view(), name="cloze-test"),
    path("cloze/<uuid:pk>", Cloze_TestUpdate.as_view(), name="cloze-test"),

    path("image-cloze/", ImageCloze_TestView.as_view(), name="image-cloze-test"),
    path("true-false/", True_False_TestView.as_view(), name="true-false"),
    path("true-false/<uuid:pk>", True_False_TestRetriveView.as_view(), name="true-false"),

    path("exam/", ExamListView.as_view(), name='exam'),
    path("exam/<uuid:pk>", ExamDetailsView.as_view(), name='exam-details'),

    path("check/", QuizCheckAPIView.as_view(), name='check'),

    path("import-quiz/", ExcelQuizUploadAPIView.as_view(), name='import-quiz'),

    path("exam-registration/", ExamRegistrationListCreateAPIView.as_view(), name='exam-registration'),
    path("registration/no-pg/", ExamRegistrationNoPgAPIView.as_view(), name='registration'),


    path("exam-students/", ExamRegisteredStudentAPIView.as_view(), name='exam-students'),

    path("exam-certificats/",ExamCertificateAPIView.as_view(), name='exam-certificates'),


    path("exam-subject/",ExamSubjectListCreate.as_view(), name='exam-subject'),
    path("exam-subject/<uuid:pk>/",ExamSubjectDetail.as_view()),

    path("student-option/",ExamOptionCreate.as_view(), name='student-option'),
]
