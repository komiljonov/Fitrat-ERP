import pandas as pd
from django.db import transaction
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from icecream import ic
from openpyxl.reader.excel import load_workbook
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .check_serializers import QuizCheckSerializer
from .models import Fill_gaps, Vocabulary, Pairs, MatchPairs, Exam, QuizGaps, Answer
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer, FillGapsSerializer, \
    VocabularySerializer, PairsSerializer, MatchPairsSerializer, ExamSerializer, \
    QuizGapsSerializer, AnswerSerializer
from ..homeworks.models import Homework
from ..mastering.models import Mastering
from ..shop.models import Points
from ..student.models import Student
from ..subject.models import Theme
from ...finances.compensation.models import Point


class QuizCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Check Quiz Answers",
        operation_description="Submit a complete set of answers for a quiz, and "
                              "receive feedback on which answers are correct.",
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
        section_counts = {
            "multiple_choice": {"correct": 0, "wrong": 0},
            "fill_gaps": {"correct": 0, "wrong": 0},
            "vocabularies": {"correct": 0, "wrong": 0},
            "match_pairs": {"correct": 0, "wrong": 0},
        }

        results = {
            "details": {
                "multiple_choice": [],
                "fill_gaps": [],
                "vocabularies": [],
                "match_pairs": [],
            }
        }

        # Optional: fetch test from serializer if it's passed
        quiz = get_object_or_404(Quiz, id=data.get("quiz_id"))

        # 1. Multiple Choice
        for item in data.get("multiple_choice", []):
            question = Question.objects.get(id=item["question_id"])
            correct_answers = question.answers.filter(is_correct=True)
            is_correct = correct_answers.filter(id=item["answer_id"]).exists()

            if is_correct:
                total_correct += 1
                section_counts["multiple_choice"]["correct"] += 1
            else:
                total_wrong += 1
                section_counts["multiple_choice"]["wrong"] += 1

            results["details"]["multiple_choice"].append({
                "question_id": str(item["question_id"]),
                "correct": is_correct,
                "your_answer": str(item["answer_id"]),
                "correct_answers": [str(a.id) for a in correct_answers]
            })

        # 2. Fill Gaps (Repeat similar logic)
        for item in data.get("fill_gaps", []):
            fill = Fill_gaps.objects.get(id=item["fill_id"])
            correct_gaps = [gap.name for gap in fill.gaps.all()]
            is_correct = correct_gaps == item["gaps"]

            if is_correct:
                total_correct += 1
                section_counts["fill_gaps"]["correct"] += 1
            else:
                total_wrong += 1
                section_counts["fill_gaps"]["wrong"] += 1

            results["details"]["fill_gaps"].append({
                "fill_id": str(item["fill_id"]),
                "correct": is_correct,
                "your_gaps": item["gaps"],
                "correct_gaps": correct_gaps
            })

        # 3. Vocabulary (Repeat similar logic)
        for item in data.get("vocabularies", []):
            vocab = Vocabulary.objects.get(id=item["vocab_id"])
            en = (item.get("english") or "").lower()
            uz = (item.get("uzbek") or "").lower()

            correct_en = (vocab.in_english or "").lower() == en
            correct_uz = (vocab.in_uzbek or "").lower() == uz
            is_correct = correct_en and correct_uz

            if is_correct:
                total_correct += 1
                section_counts["vocabularies"]["correct"] += 1
            else:
                total_wrong += 1
                section_counts["vocabularies"]["wrong"] += 1

            results["details"]["vocabularies"].append({
                "vocab_id": str(item["vocab_id"]),
                "correct": is_correct,
                "your_english": item.get("english"),
                "your_uzbek": item.get("uzbek"),
                "correct_english": vocab.in_english,
                "correct_uzbek": vocab.in_uzbek
            })

        # 4. Match Pairs (Repeat similar logic)
        for item in data.get("match_pairs", []):
            match = MatchPairs.objects.get(id=item["match_id"])
            correct_map = {p.pair: p.choice for p in match.pairs.all()}
            is_correct = True
            wrong_items = []

            for pair in item["pairs"]:
                if correct_map.get(pair["left"]) != pair["right"]:
                    is_correct = False
                    wrong_items.append(pair)

            if is_correct:
                total_correct += 1
                section_counts["match_pairs"]["correct"] += 1
            else:
                total_wrong += 1
                section_counts["match_pairs"]["wrong"] += 1

            results["details"]["match_pairs"].append({
                "match_id": str(item["match_id"]),
                "correct": is_correct,
                "your_pairs": item["pairs"],
                "correct_pairs": [{"left": k, "right": v} for k, v in correct_map.items()],
                "wrong_items": wrong_items
            })

        total_questions = total_correct + total_wrong
        ball = round((total_correct / total_questions) * 100, 2) if total_questions > 0 else 0.0

        results["summary"] = {
            "total_questions": total_questions,
            "correct_count": total_correct,
            "wrong_count": total_wrong,
            "ball": ball
        }

        student = Student.objects.filter(user=request.user).first()

        theme = data.get("theme")
        theme = Theme.objects.get(id=theme)
        mastering = Mastering.objects.create(
            theme=theme,
            lid=None,
            student=student,
            test=quiz,
            ball=ball
        )
        if mastering and mastering.ball >= 75:
            homework = Homework.objects.filter(theme=theme).first()
            point = Points.objects.create(
                point=20,
                from_test=mastering,
                from_homework=homework,
                student=student,
                comment=f"{homework.theme.title} mavzusining vazifalarini"
                        f" bajarganligi uchun 20 ball taqdim etildi !"
            )
            ic(f"{point} object has created ...")

            ic(mastering)

        return Response(results)


class QuizListCreateView(ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        queryset = Quiz.objects.all()
        theme = self.request.query_params.get("theme")
        type = self.request.GET.get("type")

        if type:
            queryset = queryset.filter(type=type)
        if theme:
            queryset = queryset.filter(theme__id=theme)
        return queryset

    def perform_create(self, serializer):
        quiz = serializer.save()
        self.update_students_count(quiz)


    def update_students_count(self, quiz):
        if quiz.students_excel and quiz.students_excel.file:
            try:
                df = pd.read_excel(quiz.students_excel.file)
                quiz.students_count = len(df)
                quiz.save(update_fields=['students_count'])
            except Exception as e:
                # optionally: log the error
                print(f"Failed to parse Excel for quiz {quiz.id}: {e}")


class QuizRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer

    def perform_update(self, serializer):
        quiz = serializer.save()

        file_id = self.request.data.get("students_excel")  # ✅ this is UUID from frontend
        if file_id:
            from ...upload.models import File  # or your correct File model path

            try:
                file_instance = File.objects.get(id=file_id)
                self.update_students_count_from_file(quiz, file_instance.file)
                print("✅ Student count updated from Excel")
            except File.DoesNotExist:
                print(f"❌ File not found for ID: {file_id}")
            except Exception as e:
                print(f"❌ Error updating student count: {e}")

    def update_students_count_from_file(self, quiz, file_obj):
        try:
            df = pd.read_excel(file_obj)
            quiz.students_count = len(df)
            quiz.save(update_fields=['students_count'])
            print(f"✅ ROWS COUNTED: {len(df)}")
        except Exception as e:
            print(f"❌ Failed to parse Excel for quiz {quiz.id}: {e}")

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


class ExcelQuizUploadAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Import Quiz Questions from Excel",
        operation_description="Upload an Excel file containing questions and answers to import them into the system.",
        manual_parameters=[
            openapi.Parameter(
                name='file',
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                required=True,
                description="Excel file (.xlsx) with a 'Questions' sheet"
            )
        ],
        responses={200: openapi.Response(description="Import result summary")}
    )
    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            wb = load_workbook(filename=file_obj)
            ws = wb.active

            created_questions = 0
            quiz_map = {}

            with transaction.atomic():
                for row in ws.iter_rows(min_row=2, values_only=True):  # Skip header
                    quiz_title, question_text, answer_text, is_correct = row

                    if not all([quiz_title, question_text, answer_text]):
                        continue

                    # Get or create quiz
                    quiz = quiz_map.get(quiz_title)
                    if not quiz:
                        quiz, _ = Quiz.objects.get_or_create(title=quiz_title)
                        quiz_map[quiz_title] = quiz

                    # Get or create QuizGaps for question text
                    gap, _ = QuizGaps.objects.get_or_create(name=question_text)

                    # Get or create Question
                    question = Question.objects.filter(text=gap, quiz=quiz).first()
                    if not question:
                        question = Question.objects.create(text=gap, quiz=quiz)

                    # Get or create Answer
                    answer, created = Answer.objects.get_or_create(text=answer_text)
                    if created:
                        answer.is_correct = str(is_correct).strip().lower() in ["true", "1", "yes"]
                        answer.save()

                    # Add answer to question
                    question.answers.add(answer)

                    created_questions += 1

            return Response({
                "message": "Quiz imported successfully",
                "quizzes_created": len(quiz_map),
                "questions_processed": created_questions
            })

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
