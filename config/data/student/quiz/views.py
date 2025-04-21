from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .check_serializers import QuizCheckSerializer
from .models import Fill_gaps, Vocabulary, Pairs, MatchPairs, Exam, QuizGaps, Answer
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer, FillGapsSerializer, \
    VocabularySerializer, PairsSerializer, MatchPairsSerializer, ExamSerializer, \
    QuizGapsSerializer, AnswerSerializer


class QuizCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Check Quiz Answers",
        operation_description="Submit a complete set of answers for a quiz, and receive feedback on which answers are correct.",
        request_body=QuizCheckSerializer,
        responses={200: openapi.Response(
            description="Result summary and detailed correctness per question type"
        )}
    )

    def post(self, request):
        serializer = QuizCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        total_correct = 0
        total_wrong = 0

        results = {
            "summary": {
                "correct_count": 0,
                "wrong_count": 0
            },
            "details": {
                "multiple_choice": [],
                "fill_gaps": [],
                "vocabularies": [],
                "listening": [],
                "match_pairs": [],
            }
        }

        # 1. Multiple Choice
        for item in data.get("multiple_choice", []):
            question = Question.objects.get(id=item["question_id"])
            correct_answers = question.answers.filter(is_correct=True)
            is_correct = correct_answers.filter(id=item["answer_id"]).exists()

            if is_correct:
                total_correct += 1
            else:
                total_wrong += 1

            results["details"]["multiple_choice"].append({
                "question_id": str(item["question_id"]),
                "correct": is_correct,
                "your_answer": str(item["answer_id"]),
                "correct_answers": [str(a.id) for a in correct_answers]
            })

        # 2. Fill Gaps
        for item in data.get("fill_gaps", []):
            fill = Fill_gaps.objects.get(id=item["fill_id"])
            correct_gaps = [gap.name for gap in fill.gaps.all()]
            is_correct = correct_gaps == item["gaps"]

            if is_correct:
                total_correct += 1
            else:
                total_wrong += 1

            results["details"]["fill_gaps"].append({
                "fill_id": str(item["fill_id"]),
                "correct": is_correct,
                "your_gaps": item["gaps"],
                "correct_gaps": correct_gaps
            })

        # 3. Vocabulary
        for item in data.get("vocabularies", []):
            vocab = Vocabulary.objects.get(id=item["vocab_id"])
            en = (item.get("english") or "").lower()
            uz = (item.get("uzbek") or "").lower()

            correct_en = (vocab.in_english or "").lower() == en
            correct_uz = (vocab.in_uzbek or "").lower() == uz
            is_correct = correct_en and correct_uz

            if is_correct:
                total_correct += 1
            else:
                total_wrong += 1

            results["details"]["vocabularies"].append({
                "vocab_id": str(item["vocab_id"]),
                "correct": is_correct,
                "your_english": item.get("english"),
                "your_uzbek": item.get("uzbek"),
                "correct_english": vocab.in_english,
                "correct_uzbek": vocab.in_uzbek
            })

        # 4. Listening
        # for item in data.get("listening", []):
        #     listen = Listening.objects.get(id=item["listening_id"])
        #     correct_answers = listen.answers.filter(is_correct=True)
        #     is_correct = correct_answers.filter(id=item["answer_id"]).exists()
        #
        #     if is_correct:
        #         total_correct += 1
        #     else:
        #         total_wrong += 1
        #
        #     results["details"]["listening"].append({
        #         "listening_id": str(item["listening_id"]),
        #         "correct": is_correct,
        #         "your_answer": str(item["answer_id"]),
        #         "correct_answers": [str(a.id) for a in correct_answers]
        #     })

        # 5. Match Pairs
        for item in data.get("match_pairs", []):
            match = MatchPairs.objects.get(id=item["match_id"])
            correct_map = {p.pair: p.choice for p in match.pairs.all()}
            is_correct = True
            wrong_items = []

            for pair in item["pairs"]:
                left = pair["left"]
                right = pair["right"]
                if correct_map.get(left) != right:
                    is_correct = False
                    wrong_items.append(pair)

            if is_correct:
                total_correct += 1
            else:
                total_wrong += 1

            results["details"]["match_pairs"].append({
                "match_id": str(item["match_id"]),
                "correct": is_correct,
                "your_pairs": item["pairs"],
                "correct_pairs": [{"left": k, "right": v} for k, v in correct_map.items()],
                "wrong_items": wrong_items if not is_correct else []
            })

        results["summary"]["correct_count"] = total_correct
        results["summary"]["wrong_count"] = total_wrong

        return Response(results)

class QuizListCreateView(ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def get_queryset(self):

        queryset = Quiz.objects.all()

        theme = self.request.query_params.get("theme")
        if theme:
            queryset = queryset.filter(theme__id=theme)
        return queryset



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
