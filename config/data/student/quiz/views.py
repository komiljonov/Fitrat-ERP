from datetime import datetime, timedelta

import openpyxl
import pandas as pd
from django.db import transaction
from django.dispatch.dispatcher import logger
from django.http import HttpResponse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from openpyxl.reader.excel import load_workbook
from openpyxl.styles import PatternFill
from openpyxl.utils import get_column_letter
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, get_object_or_404, ListAPIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .check_serializers import QuizCheckSerializer
from .models import Fill_gaps, Vocabulary, Pairs, MatchPairs, Exam, QuizGaps, Answer, ExamRegistration, ObjectiveTest, \
    Cloze_Test, ImageObjectiveTest, True_False
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer, FillGapsSerializer, \
    VocabularySerializer, PairsSerializer, MatchPairsSerializer, ExamSerializer, \
    QuizGapsSerializer, AnswerSerializer, ExamRegistrationSerializer, ObjectiveTestSerializer, Cloze_TestSerializer, \
    ImageObjectiveTestSerializer, True_FalseSerializer
from ..homeworks.models import Homework
from ..mastering.models import Mastering
from ..shop.models import Points
from ..student.models import Student
from ..subject.models import Theme
from ...account.models import CustomUser


class QuizCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Check Quiz Answers",
        operation_description="Submit answers to a quiz and get results.",
        request_body=QuizCheckSerializer,
        responses={200: openapi.Response(
            description="Quiz result summary with section breakdown."
        )}
    )
    def post(self, request):
        serializer = QuizCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        quiz = get_object_or_404(Quiz, id=data.get("quiz_id"))
        student = Student.objects.filter(user=request.user).first()
        theme = get_object_or_404(Theme, id=data.get("theme"))

        results = {
            "details": {},
            "summary": {
                "total_questions": 0,
                "correct_count": 0,
                "wrong_count": 0,
                "ball": 0.0,
                "section_breakdown": {}
            }
        }
        quiz_questions = QuizSerializer(quiz).data["questions"]

        for question in quiz_questions:
            qtype = question["type"]
            qid = question["id"]

            if qtype not in results["details"]:
                results["details"][qtype] = []
                results["summary"]["section_breakdown"][qtype] = {
                    "correct": 0,
                    "wrong": 0
                }

            user_answer = self._find_user_answer(data, qtype, qid)
            if not user_answer:
                self._record_missing_answer(results, qtype, qid)
                continue

            is_correct, result_data = self._check_answer(question, user_answer)
            logger.debug(f"Question {qid} result: {is_correct}")

            if is_correct:
                results["summary"]["correct_count"] += 1
                results["summary"]["section_breakdown"][qtype]["correct"] += 1
            else:
                results["summary"]["wrong_count"] += 1
                results["summary"]["section_breakdown"][qtype]["wrong"] += 1

            results["details"][qtype].append(result_data)

        total = results["summary"]["correct_count"] + results["summary"]["wrong_count"]
        results["summary"]["total_questions"] = total
        results["summary"]["ball"] = round(
            (results["summary"]["correct_count"] / total * 100), 2
        ) if total > 0 else 0.0

        self._create_mastering_record(theme, student, quiz, results["summary"]["ball"])

        return Response(results)

    def _find_user_answer(self, data, qtype, qid):
        if qtype not in data:
            return None

        id_fields = {
            'standard': 'question_id',
            'multiple_choice': 'question_id',
            'fill_gaps': 'fill_id',
            'vocabularies': 'vocab_id',
            'listening': 'listening_id',
            'match_pairs': 'match_id',
            'objective_test': 'objective_id',
            'cloze_test': 'cloze_id',
            'image_objective_test': 'image_objective_id',
            'image_objective': 'image_objective_id',
            'true_false': 'true_false_id'
        }

        id_field = id_fields.get(qtype, 'question_id')

        for answer in data[qtype]:
            answer_id = str(answer.get(id_field))
            if answer_id == str(qid):
                return answer

        return None

    def _record_missing_answer(self, results, qtype, qid):
        results["summary"]["wrong_count"] += 1
        results["summary"]["section_breakdown"][qtype]["wrong"] += 1
        results["details"][qtype].append({
            "id": qid,
            "correct": False,
            "error": "No answer submitted"
        })

    def _check_answer(self, question, user_answer):
        qtype = question["type"]

        # Handle image_objective as image_objective_test
        if qtype == "image_objective":
            qtype = "image_objective_test"

        checker = getattr(self, f"check_{qtype}", None)
        if not checker:
            return False, {"error": "Unsupported question type", "id": question["id"]}

        try:
            return checker(question, user_answer)
        except Exception as e:
            return False, {"error": str(e), "id": question["id"]}

    def check_standard(self, question, user_answer):
        try:
            # Get correct answer ID
            correct_answer_id = None
            if "answer" in question:
                correct_answer_id = question["answer"]
            elif "answers" in question:
                correct_answer = next(
                    (a for a in question["answers"] if a.get("is_correct")),
                    None
                )
                if correct_answer:
                    correct_answer_id = correct_answer["id"]

            user_answer_id = user_answer.get("answer_id")
            is_correct = str(user_answer_id) == str(correct_answer_id)

            response_data = {
                "id": question["id"],
                "correct": is_correct,
                "user_answer": user_answer_id,
                "correct_answer": correct_answer_id,
                "answers": question["answers"],
                "question_text": question.get("text", {}).get("name") or
                                 question.get("question", {}).get("name")
            }

            if not is_correct and correct_answer_id and "answers" in question:
                correct_answer = next(
                    (a for a in question["answers"] if str(a["id"]) == str(correct_answer_id)),
                    None
                )
                if correct_answer:
                    response_data["correct_answer_text"] = correct_answer.get("text")

            return is_correct, response_data

        except Exception as e:
            logger.error(f"Error processing standard question: {str(e)}")
            return False, {
                "id": question["id"],
                "correct": False,
                "error": str(e),
                "user_answer": user_answer.get("answer_id"),
                "correct_answer": "Error processing correct answer"
            }

    def check_multiple_choice(self, question, user_answer):
        return self.check_standard(question, user_answer)

    def check_true_false(self, question, user_answer):
        correct_answer = question.get("answer").lower() == "true"
        user_choice = user_answer.get("choice")
        return user_choice == correct_answer, {
            "id": question["id"],
            "question_text": question.get("text", {}).get("name"),
            "correct": user_choice == correct_answer,
            "user_answer": user_choice,
            "correct_answer": correct_answer
        }

    def check_fill_gaps(self, question, user_answer):
        correct_gaps = [gap["name"] for gap in question.get("gaps", [])]
        user_gaps = user_answer.get("gaps", [])

        if len(correct_gaps) != len(user_gaps):
            return False, {
                "id": question["id"],
                "correct": False,
                "user_answer": user_gaps,
                "correct_answer": correct_gaps
            }

        all_correct = all(str(user_gap).lower() == str(correct_gap).lower()
                          for user_gap, correct_gap in zip(user_gaps, correct_gaps))

        return all_correct, {
            "id": question["id"],
            "correct": all_correct,
            "user_answer": user_gaps,
            "correct_answer": correct_gaps
        }

    def check_objective_test(self, question, user_answer):
        try:
            # Get correct answer text
            correct_answer = question.get("answer", "")
            if not correct_answer and "answers" in question:
                correct_answer = next(
                    (a["text"] for a in question["answers"] if a.get("is_correct")),
                    ""
                )

            user_answer_text = user_answer.get("answer_ids", "")

            is_correct = str(user_answer_text).strip().lower() == str(correct_answer).strip().lower()

            return is_correct, {
                "id": question["id"],
                "correct": is_correct,
                "user_answer": user_answer_text,
                "correct_answer": correct_answer
            }
        except Exception as e:
            return False, {
                "id": question["id"],
                "correct": False,
                "error": str(e),
                "user_answer": user_answer.get("answer", ""),
                "correct_answer": "Error processing correct answer"
            }

    def check_cloze_test(self, question, user_answer):
        try:
            # Get correct sequence (reversed from DB storage)
            db_sequence = [q["name"] for q in question.get("questions", [])]
            correct_sequence = db_sequence[::-1]  # Reverse to get correct order

            user_sequence = user_answer.get("word_sequence", [])

            is_correct = user_sequence == correct_sequence

            return is_correct, {
                "id": question["id"],
                "correct": is_correct,
                "user_answer": user_sequence,
                "correct_answer": correct_sequence
            }
        except Exception as e:
            return False, {
                "id": question["id"],
                "correct": False,
                "error": str(e),
                "user_answer": user_answer.get("word_sequence", []),
                "correct_answer": "Error processing correct sequence"
            }

    def check_image_objective_test(self, question, user_answer):
        try:
            # Get correct answer text
            correct_answer = question.get("answer", "")

            correct_answer = Answer.objects.filter(id=correct_answer).first()

            # Get user's text answer
            user_answer_text = user_answer.get("answer", "")

            # Compare answers case-insensitively and with stripped whitespace
            is_correct = str(user_answer_text).strip().lower() == str(correct_answer.text).strip().lower()

            image = ImageObjectiveTest.objects.filter(answer=correct_answer).first()
            print(image)
            return is_correct, {
                "id": question["id"],
                "correct": is_correct,
                "image": image.image.url if image and image.image else None,
                "user_answer": user_answer_text,
                "correct_answer": correct_answer.text
            }
        except Exception as e:
            logger.error(f"Error processing image objective test question: {str(e)}")
            correct_answer = question.get("answer", "")

            correct_answer = Answer.objects.filter(id=correct_answer).first()
            image = ImageObjectiveTest.objects.filter(answer=correct_answer).first()
            print(image)
            return False, {
                "id": question["id"],
                "correct": False,
                "image": image.image.url if image and image.image else None,
                "error": str(e),
                "user_answer": user_answer.get("answer", ""),
                "correct_answer": "Error processing correct answer"
            }

    def check_match_pairs(self, question, user_answer):
        try:
            match_pairs_id = question.get("id")
            match_pairs = MatchPairs.objects.prefetch_related('pairs').get(id=match_pairs_id)
            all_pairs = list(match_pairs.pairs.all())

            # Split into left and right items
            left_items = [pair for pair in all_pairs if pair.choice == "Left"]
            right_items = [pair for pair in all_pairs if pair.choice == "Right"]

            # Validate pairs
            if not left_items or not right_items:
                raise ValueError("Question must contain both left and right pairs")
            if len(left_items) != len(right_items):
                raise ValueError("Left and right items must be equal in number")

            # Create mappings
            left_map = {str(item.id): item.pair for item in left_items}
            right_map = {str(item.id): item.pair for item in right_items}

            # Create key mappings for validation
            left_key_map = {str(item.id): item.key for item in left_items}
            right_key_map = {str(item.id): item.key for item in right_items}

            # Build correct mapping based on matching keys
            # Group left and right items by their keys
            left_by_key = {item.key: str(item.id) for item in left_items}
            right_by_key = {item.key: str(item.id) for item in right_items}

            # Create correct mapping: left_id -> right_id for items with same key
            correct_mapping = {}
            for key in left_by_key.keys():
                if key in right_by_key:
                    correct_mapping[left_by_key[key]] = right_by_key[key]

            # Validate that all keys have matches
            if len(correct_mapping) != len(left_items):
                raise ValueError("Not all left items have corresponding right items with matching keys")

            # Validate user input
            user_pairs = user_answer.get("pairs", [])
            if not user_pairs:
                return False, self._build_match_response(
                    question["id"], False, "No pairs submitted", [], correct_mapping, left_map, right_map
                )

            if len(user_pairs) != len(left_items):
                return False, self._build_match_response(
                    question["id"], False, f"Expected {len(left_items)} pairs", user_pairs, correct_mapping, left_map,
                    right_map
                )

            # Check each pair
            results = []
            used_left = set()
            used_right = set()
            all_correct = True

            for pair in user_pairs:
                left_id = str(pair.get("left_id", ""))
                right_id = str(pair.get("right_id", ""))
                is_correct = False
                error = None

                # Validate IDs
                if left_id not in left_map:
                    error = "Invalid left_id"
                elif right_id not in right_map:
                    error = "Invalid right_id"
                elif left_id in used_left:
                    error = "Duplicate left_id"
                elif right_id in used_right:
                    error = "Duplicate right_id"
                else:
                    used_left.add(left_id)
                    used_right.add(right_id)
                    # Check if the keys match (this is the key change)
                    left_key = left_key_map.get(left_id)
                    right_key = right_key_map.get(right_id)
                    is_correct = (left_key == right_key)

                if error or not is_correct:
                    all_correct = False

                results.append({
                    "left_id": left_id,
                    "left_text": left_map.get(left_id),
                    "left_key": left_key_map.get(left_id),
                    "right_id": right_id,
                    "right_text": right_map.get(right_id),
                    "right_key": right_key_map.get(right_id),
                    "is_correct": is_correct,
                    **({"error": error} if error else {})
                })

            return all_correct, self._build_match_response(
                question["id"], all_correct, None, user_pairs, correct_mapping, left_map, right_map, results
            )

        except MatchPairs.DoesNotExist:
            return False, {"error": "Question not found"}
        except Exception as e:
            return False, {"error": str(e)}

    def _build_match_response(self, question_id, is_correct, error, user_pairs, correct_mapping, left_map, right_map,
                              pair_results=None):
        """Build consistent response format with all needed information"""
        response = {
            "id": question_id,
            "correct": is_correct,
            "user_answer": user_pairs,
            "correct_answer": [
                {
                    "left_id": left_id,
                    "left_text": left_map.get(left_id),
                    "right_id": right_id,
                    "right_text": right_map.get(right_id)
                }
                for left_id, right_id in correct_mapping.items()
            ]
        }

        if error:
            response["error"] = error
        if pair_results:
            response["pair_results"] = pair_results

        return response

    def _create_mastering_record(self, theme, student, quiz, ball):
        """Create mastering record and award points if eligible"""
        if not student:
            return

        try:
            mastering = Mastering.objects.create(
                theme=theme,
                lid=None,
                student=student,
                test=quiz,
                ball=ball
            )

            if homework := Homework.objects.filter(theme=theme).first():
                Points.objects.create(
                    point=ball,
                    from_test=mastering,
                    from_homework=homework,
                    student=student,
                    comment=f"{homework.theme.title} mavzusining vazifalarini bajarganligi uchun {ball} ball taqdim etildi!"
                )
        except Exception as e:
            logger.error(f"Error creating mastering record: {str(e)}")


class ObjectiveTestView(ListCreateAPIView):
    queryset = ObjectiveTest.objects.all()
    serializer_class = ObjectiveTestSerializer


class Cloze_TestView(ListCreateAPIView):
    queryset = Cloze_Test.objects.all()
    serializer_class = Cloze_TestSerializer


class ImageCloze_TestView(ListCreateAPIView):
    queryset = ImageObjectiveTest.objects.all()
    serializer_class = ImageObjectiveTestSerializer


class True_False_TestView(ListCreateAPIView):
    queryset = True_False.objects.all()
    serializer_class = True_FalseSerializer


class True_False_TestRetriveView(RetrieveUpdateDestroyAPIView):
    queryset = True_False.objects.all()
    serializer_class = True_FalseSerializer


class QuizListCreateView(ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        queryset = Quiz.objects.all()
        theme = self.request.GET.get("theme")
        homework = self.request.GET.get("homework")
        search = self.request.GET.get("search")

        if homework:
            queryset = queryset.filter(homework__id=homework)

        if theme:
            queryset = queryset.filter(theme__id=theme)

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset


class QuizListPgView(ListAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    pagination_class = None

    def get_queryset(self):
        queryset = Quiz.objects.all()
        theme = self.request.GET.get("theme")
        homework = self.request.GET.get("homework")
        search = self.request.GET.get("search")

        if homework:
            queryset = queryset.filter(homework__id=homework)

        if theme:
            queryset = queryset.filter(theme__id=theme)

        if search:
            queryset = queryset.filter(title__icontains=search)

        return queryset

    def get_paginated_response(self, data):
        return Response(data)


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
        quiz = self.request.GET.get("quiz")
        choice = self.request.GET.get("choice")
        type = self.request.GET.get("type")
        is_mandatory = self.request.GET.get("is_mandatory")
        students = self.request.GET.get("students")
        subject = self.request.GET.get("subject")
        date = self.request.GET.get("date")
        start_time = self.request.GET.get("start_time")
        end_time = self.request.GET.get("end_time")
        homework = self.request.GET.get("homework")
        is_language = self.request.GET.get("is_language")
        lang_group = self.request.GET.get("lang_group")
        options = self.request.GET.get("options")

        queryset = Exam.objects.all()

        user = CustomUser.objects.filter(id=self.request.user.id).first()

        if user.role == "TEACHER":
            three_days_later = datetime.today() + timedelta(days=3)
            queryset = queryset.filter(date__gt=three_days_later)

        if user.role == "Student":
            two_days_later = datetime.today() + timedelta(days=2)
            queryset = queryset.filter(date__gt=two_days_later)

        if options:
            queryset = queryset.filter(options=options)
        if is_language:
            queryset = queryset.filter(is_language=is_language.capitalize())
        if lang_group:
            queryset = queryset.filter(lang_group=lang_group)
        if quiz:
            queryset = queryset.filter(quiz__id=quiz)
        if choice:
            queryset = queryset.filter(choice=choice)
        if type:
            queryset = queryset.filter(type=type)
        if is_mandatory:
            queryset = queryset.filter(is_mandatory=is_mandatory.capitalize())
        if students:
            queryset = queryset.filter(students__id__in=students)
        if subject:
            queryset = queryset.filter(subject__id__in=subject)
        if date:
            queryset = queryset.filter(date=date)
        if start_time:
            queryset = queryset.filter(start_time__gte=start_time)
        if start_time and end_time:
            queryset = queryset.filter(start_time__gte=start_time, end_time__lte=end_time)
        if homework:
            queryset = queryset.filter(homework__id=homework)

        return queryset

    def perform_create(self, serializer):
        quiz = serializer.save()
        self.update_students_count(quiz)

    def update_students_count(self, quiz):
        if quiz.students_xml and quiz.students_xml.file:
            try:
                df = pd.read_excel(quiz.students_xml.file)
                quiz.students_count = len(df)
                quiz.save(update_fields=['students_count'])
            except Exception as e:
                # optionally: log the error
                print(f"Failed to parse Excel for quiz {quiz.id}: {e}")


class ExamDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [IsAuthenticated]

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


class ExamRegistrationListCreateAPIView(ListCreateAPIView):
    queryset = ExamRegistration.objects.all()
    serializer_class = ExamRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = ExamRegistration.objects.all()

        student = self.request.GET.get("student")
        exam = self.request.GET.get("exam")
        status = self.request.GET.get("status")
        is_participating = self.request.GET.get("is_participating")
        option = self.request.GET.get("option")
        has_certificate = self.request.GET.get("has_certificate")

        if has_certificate:
            qs = qs.filter(has_certificate=has_certificate.capitalize())
        if student:
            qs = qs.filter(student__id=student)
        if exam:
            qs = qs.filter(exam__id=exam)
        if status:
            qs = qs.filter(status=status)
        if is_participating:
            qs = qs.filter(is_participating=is_participating.capitalize())
        if option:
            qs = qs.filter(option=option)
        return qs


class ExamRegisteredStudentAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_summary="Export Registered Students to Excel",
        operation_description="Download an Excel file containing registered students for a specific exam.",
        manual_parameters=[
            openapi.Parameter(
                name='exam_id',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
                description="ID of the exam"
            )
        ],
        responses={200: openapi.Response(description="Excel file with registered students")}
    )
    def get(self, request):
        exam_id = request.GET.get("exam_id")
        if not exam_id:
            return Response({"detail": "Missing 'exam_id' parameter."}, status=400)

        try:
            exam = Exam.objects.get(id=exam_id)
        except Exam.DoesNotExist:
            return Response({"detail": "Exam not found."}, status=404)

        registrations = ExamRegistration.objects.filter(exam=exam).select_related('student')

        # Sort by is_participating (True first)
        registrations = sorted(registrations, key=lambda r: not r.is_participating)

        # Create Excel workbook
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Registered Students"

        headers = [
            "F.I.O", "Telefon raqami", "Ro'yxatdan o'tish", "Imtihonda qatnashadimi?",
            "Ball", "Talaba izohi", "Variant", "Sertifikati egasimi"
        ]
        ws.append(headers)

        # Define fill styles
        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")  # light green
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # light red

        for reg in registrations:
            student = reg.student
            row_data = [
                f"{student.first_name} {student.last_name}",
                getattr(student, 'phone', ''),
                "Faol" if reg.status == "Active" else "Yakunlangan",
                "Ha" if reg.is_participating else "Yo'q",
                reg.mark,
                reg.student_comment,
                reg.option,
                "Ha" if reg.has_certificate else "Yo'q"
            ]
            row = ws.append(row_data)

            # Apply row coloring
            fill = green_fill if reg.is_participating else red_fill
            for col in range(1, len(row_data) + 1):
                ws.cell(row=ws.max_row, column=col).fill = fill

        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = get_column_letter(column[0].column)
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2

        # Prepare response
        response = HttpResponse(
            content_type="appl  ication/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        filename = f"registered_students_exam_{exam.date}.xlsx"
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        wb.save(response)
        return response
