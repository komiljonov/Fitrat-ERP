from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Fill_gaps, Vocabulary, Pairs, MatchPairs, Exam, QuizGaps, Answer
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer, FillGapsSerializer, \
    VocabularySerializer, PairsSerializer, MatchPairsSerializer, ExamSerializer, \
    QuizGapsSerializer, AnswerSerializer


class QuizListCreateView(ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuizRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

class AnswerListCreateView(ListCreateAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]

class AnswerRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [IsAuthenticated]


class QuestionsListCreateView(ListCreateAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]

class QuestionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAuthenticated]



class FillGapsView(ListCreateAPIView):
    queryset = Fill_gaps.objects.all()
    serializer_class = FillGapsSerializer
    permission_classes = [IsAuthenticated]


class FillGapsDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Fill_gaps.objects.all()
    serializer_class = FillGapsSerializer
    permission_classes = [IsAuthenticated]




class VocabularyListView(ListCreateAPIView):
    queryset = Vocabulary.objects.all()
    serializer_class = VocabularySerializer
    permission_classes = [IsAuthenticated]


class VocabularyDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Vocabulary.objects.all()
    serializer_class = VocabularySerializer
    permission_classes = [IsAuthenticated]


class LeftPairsListView(ListCreateAPIView):
    queryset = Pairs.objects.all()
    serializer_class = PairsSerializer
    permission_classes = [IsAuthenticated]


class LeftPairsDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Pairs.objects.all()
    serializer_class = PairsSerializer
    permission_classes = [IsAuthenticated]

class MatchPairsListView(ListCreateAPIView):
    queryset = MatchPairs.objects.all()
    serializer_class = MatchPairsSerializer
    permission_classes = [IsAuthenticated]


class MatchPairsDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = MatchPairs.objects.all()
    serializer_class = MatchPairsSerializer
    permission_classes = [IsAuthenticated]


class ExamListView(ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id = self.request.query_params.get("id")
        search = self.request.query_params.get("search")

        queryset = Exam.objects.all()

        if id:
            queryset = queryset.filter(quiz__id=id)

        return queryset


class ExamDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]


class QuizGapsListView(ListCreateAPIView):
    queryset = QuizGaps.objects.all()
    serializer_class = QuizGapsSerializer
    permission_classes = [IsAuthenticated]


class QuizGapsDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = QuizGaps.objects.all()
    serializer_class = QuizGapsSerializer
    permission_classes = [IsAuthenticated]
