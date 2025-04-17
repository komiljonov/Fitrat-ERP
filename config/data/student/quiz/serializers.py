from rest_framework import serializers

from .models import Quiz, Question, Answer, Fill_gaps, Vocabulary, Pairs, MatchPairs
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


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
    fill_gap = serializers.SerializerMethodField()
    vocabularies = serializers.SerializerMethodField()
    match_pairs = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "questions",
            "fill_gap",
            "vocabularies",
            "match_pairs",
            "created_at",
        ]

    def get_fill_gap(self, obj):
        return Fill_gaps.objects.filter(quiz=obj)

    def get_vocabularies(self, obj):
        return Vocabulary.objects.filter(quiz=obj)

    def get_match_pairs(self, obj):
        return MatchPairs.objects.filter(quiz=obj)



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


class FillGapsSerializer(serializers.Serializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(),allow_null=True)
    question = serializers.PrimaryKeyRelatedField(queryset=Question.objects.all(),allow_null=True)

    class Meta:
        model = Fill_gaps
        fields = ["id","quiz", "question"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["quiz"] = QuizSerializer(instance.quiz).data
        rep["question"] = QuestionSerializer(instance.question).data
        return rep


class VocabularySerializer(serializers.Serializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(),allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    voice = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    class Meta:
        model = Vocabulary
        fields = [
            "id",
            "quiz",
            "photo",
            "voice",
            "in_english",
            "in_uzbek",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["quiz"] = QuizSerializer(instance.quiz).data
        rep["photo"] = FileUploadSerializer(instance.photo).data
        rep["voice"] = FileUploadSerializer(instance.voice).data
        return rep

class PairsSerializer(serializers.Serializer):
    class Meta:
        model = Pairs
        fields = [
            "id",
            "pair1",
            "pair2",
            "created_at",
        ]

class MatchPairsSerializer(serializers.Serializer):
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all(),allow_null=True)
    pair1 = serializers.PrimaryKeyRelatedField(queryset=Pairs.objects.all(),allow_null=True)
    class Meta:
        model = MatchPairs
        fields = [
            "id",
            "quiz",
            "pairs",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["quiz"] = QuizSerializer(instance.quiz).data
        rep["pairs"] = PairsSerializer(instance.pairs).data
        return rep
