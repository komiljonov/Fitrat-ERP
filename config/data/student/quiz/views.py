from rest_framework import generics, status
from rest_framework.response import Response
from .models import Quiz, Question, Answer
from .serializers import QuizSerializer, QuestionSerializer, UserAnswerSerializer


class QuizListCreateView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuizRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer


class QuestionListCreateView(generics.ListCreateAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        return Question.objects.filter(quiz_id=quiz_id)

    def perform_create(self, serializer):
        quiz_id = self.kwargs.get('quiz_pk')
        quiz = Quiz.objects.get(pk=quiz_id)
        serializer.save(quiz=quiz)


class QuestionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = QuestionSerializer

    def get_queryset(self):
        quiz_id = self.kwargs.get('quiz_pk')
        return Question.objects.filter(quiz_id=quiz_id)


class QuestionCheckAnswerView(generics.GenericAPIView):
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


class QuizBulkCheckView(generics.GenericAPIView):
    def post(self, request, quiz_pk):
        try:
            quiz = Quiz.objects.get(pk=quiz_pk)
            user_answers_data = request.data.get('user_answers')
            user_answer_serializer = UserAnswerSerializer(data=user_answers_data, many=True)

            if not user_answer_serializer.is_valid():
                return Response(user_answer_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            user_answers = user_answer_serializer.validated_data

            results = []
            correct_answers_with_questions = []
            correct_count = 0

            for user_answer in user_answers:
                question_id = user_answer['question_id']
                answer_id = user_answer['answer_id']

                try:
                    question = Question.objects.get(pk=question_id, quiz=quiz)
                    is_correct = question.check_answer(answer_id)

                    results.append({
                        'question_id': question_id,
                        'is_correct': is_correct
                    })

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
                    return Response({'error': f'Question with id {question_id} not found'},
                                    status=status.HTTP_400_BAD_REQUEST)

            score = (correct_count / len(user_answers)) * 100 if user_answers else 0

            response_data = {
                'quiz_score': score,
                'results': results,
                'correct_answers': correct_answers_with_questions
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Quiz.DoesNotExist:
            return Response({'error': 'Quiz not found'}, status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response({'error': 'user_answers are required in the request body'},
                            status=status.HTTP_400_BAD_REQUEST)

