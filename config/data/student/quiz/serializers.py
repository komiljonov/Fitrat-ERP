from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers
from .models import Quiz, Question, Answer


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ["id", "text", "is_correct"]


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "question_text", "answers"]


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ["id", "title", "description", "questions"]

class QuizImportSerializer(serializers.Serializer):
    title = serializers.CharField()
    description = serializers.CharField(required=False, allow_blank=True)
    questions = QuestionSerializer(many=True)

    def create(self, validated_data):
        quiz, created = Quiz.objects.get_or_create(
            title=validated_data['title'],
            defaults={'description': validated_data.get('description', '')}
        )

        for question_data in validated_data['questions']:
            question = Question.objects.create(
                quiz=quiz, question_text=question_data['question_text']
            )

            # Create and add answers to the question
            answers = [
                Answer.objects.create(**answer_data)
                for answer_data in question_data['answers']
            ]
            question.answers.set(answers)

        return quiz

class UserAnswerSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField()


