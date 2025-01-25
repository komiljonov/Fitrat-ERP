import pandas as pd
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListCreateAPIView,RetrieveUpdateDestroyAPIView,GenericAPIView
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Answer
from .models import Quiz, Question
from .serializers import QuizSerializer, QuestionSerializer, UserAnswerSerializer
from ..mastering.models import Mastering


class QuizListCreateView(ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuizRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuestionListCreateView(ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        return Question.objects.filter(quiz_id=quiz_id)

    def perform_create(self, serializer):
        quiz_id = self.kwargs.get('quiz_pk')
        quiz = Quiz.objects.get(pk=quiz_id)
        serializer.save(quiz=quiz)


class QuestionRetrieveUpdateDestroyView(RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        return Question.objects.filter(quiz_id=quiz_id)


class QuestionCheckAnswerView(GenericAPIView):
    def post(self, request, quiz_pk, pk):
        try:
            question = Question.objects.get(pk=pk, quiz_id=quiz_pk)
            answer_id = request.data.get('answer_id')
            is_correct = question.check_answer(answer_id)
            return Response({'is_correct': is_correct}, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'error': 'answer_id is required in the request body'}, status=status.HTTP_400_BAD_REQUEST)


class QuizBulkCheckView(GenericAPIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request, quiz_pk):
        try:
            # Ensure the quiz exists
            quiz = Quiz.objects.get(pk=quiz_pk)
            user_answers_data = request.data  # This is a list, not a dictionary

            if not isinstance(user_answers_data, list):
                return Response({'error': 'Invalid data format. Expected a list of user answers.'}, status=status.HTTP_400_BAD_REQUEST)

            # Iterate through user answers
            results = []
            correct_answers_with_questions = []
            correct_count = 0

            for user_answer in user_answers_data:
                question_id = user_answer.get('question_id')
                answer_id = user_answer.get('answer_id')

                # Ensure both question_id and answer_id are provided
                if not question_id or not answer_id:
                    return Response({'error': 'Each answer must include question_id and answer_id.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                try:
                    # Fetch the question and check the answer
                    question = Question.objects.get(pk=question_id, quiz=quiz)
                    is_correct = question.check_answer(answer_id)

                    results.append({
                        'question_id': question_id,
                        'is_correct': is_correct
                    })

                    # Track correct answers
                    if is_correct:
                        correct_count += 1
                        correct_answer = question.get_correct_answer()
                        correct_answers_with_questions.append({
                            'question_id': question.id,
                            'question_text': question.question_text,
                            'correct_answer_id': correct_answer.id,
                            'correct_answer_text': correct_answer.text
                        })

                except Question.DoesNotExist:
                    return Response({'error': f'Question with id {question_id} not found in this quiz.'},
                                    status=status.HTTP_400_BAD_REQUEST)

            # Calculate the score
            total_questions = len(user_answers_data)
            score = (correct_count / total_questions) * 100 if total_questions > 0 else 0

            create_ball = Mastering.objects.create(
                student = request.user,
                test = quiz_pk,
                ball = score,
            )
            if create_ball:
                return Response({'created': create_ball.created}, status=status.HTTP_201_CREATED)

            # Build the response
            response_data = {
                'quiz_score': score,
                'results': results,
                'correct_answers': correct_answers_with_questions
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'An unexpected error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuizImportView(CreateAPIView):
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="The Excel file containing quiz data.",
                required=True,
            )
        ],
        responses={
            201: openapi.Response(description="Quiz data imported successfully."),
            400: openapi.Response(description="Bad request. Errors in the uploaded file or its format."),
        },
    )
    def post(self, request, *args, **kwargs):
        # Get the uploaded file
        file = request.FILES.get("file")
        if not file:
            return Response({"error": "Please upload an Excel file."}, status=status.HTTP_400_BAD_REQUEST)

        # Read the Excel file into a pandas DataFrame
        try:
            data = pd.read_excel(file)
        except Exception as e:
            return Response({"error": f"Error reading Excel file: {e}"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate the file structure
        required_columns = [
            "Quiz Title",
            "Description",
            "Question Text",
            "Answer 1",
            "Answer 2",
            "Answer 3",
            "Answer 4",
            "Correct Answer",
        ]
        if not all(column in data.columns for column in required_columns):
            return Response(
                {"error": f"The Excel file must contain the following columns: {', '.join(required_columns)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create quizzes, questions, and answers
        for _, row in data.iterrows():
            quiz, _ = Quiz.objects.get_or_create(
                title=row["Quiz Title"], defaults={"description": row.get("Description", "")}
            )
            question = Question.objects.create(quiz=quiz, question_text=row["Question Text"])
            answers = [
                Answer.objects.create(text=row["Answer 1"], is_correct=row["Correct Answer"] == 1),
                Answer.objects.create(text=row["Answer 2"], is_correct=row["Correct Answer"] == 2),
                Answer.objects.create(text=row["Answer 3"], is_correct=row["Correct Answer"] == 3),
                Answer.objects.create(text=row["Answer 4"], is_correct=row["Correct Answer"] == 4),
            ]
            question.answers.set(answers)

        return Response({"message": "Quiz data imported successfully."}, status=status.HTTP_201_CREATED)
