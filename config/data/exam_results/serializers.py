
from rest_framework import serializers

from .models import UnitTest, UnitTestResult, QuizResult
from ..student.quiz.serializers import QuestionSerializer, MatchPairsSerializer, True_FalseSerializer, \
    VocabularySerializer, ObjectiveTestSerializer, Cloze_TestSerializer, ImageObjectiveTestSerializer
from ..student.student.models import Student
from ..student.subject.models import Theme
from ..student.subject.serializers import ThemeSerializer


class UnitTestSerializer(serializers.ModelSerializer):
    themes = serializers.PrimaryKeyRelatedField(many=True, queryset=Theme.objects.all(),allow_null=True)
    class Meta:
        model = UnitTest
        fields = [
            "id",
            "theme_after",
            "themes",
            "quiz",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["themes"] = ThemeSerializer(instance.themes.all(), many=True).data
        return rep


class UnitTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitTestResult
        fields = [
            "id",
            "student",
            "unit",
            "point",
            "created_at"
        ]

class QuizResultSerializer(serializers.ModelSerializer):
    match_pair = serializers.ListField(write_only=True, required=False)
    true_false = serializers.ListField(write_only=True, required=False)
    questions = serializers.ListField(write_only=True, required=False)
    cloze_test = serializers.ListField(write_only=True, required=False)
    objective = serializers.ListField(write_only=True, required=False)
    image_objective = serializers.ListField(write_only=True, required=False)
    vocabulary = serializers.ListField(write_only=True, required=False)

    standard = serializers.SerializerMethodField()
    match_pairs = serializers.SerializerMethodField()
    true_false_result = serializers.SerializerMethodField()
    vocabulary_result = serializers.SerializerMethodField()
    objective_test = serializers.SerializerMethodField()
    cloze_test_result = serializers.SerializerMethodField()
    image_objective_result = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = [
            "id", "student", "point", "created_at", "quiz",
            "questions", "match_pair", "true_false", "vocabulary",
            "objective", "cloze_test", "image_objective",
            "standard", "match_pairs", "true_false_result",
            "vocabulary_result", "objective_test",
            "cloze_test_result", "image_objective_result"
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        student = validated_data.get("student")

        if not student and request and hasattr(request.user, 'student'):
            student = Student.objects.filter(user=request.user).first()

        quiz = validated_data["quiz"]

        quiz_result = QuizResult.objects.create(student=student, quiz=quiz)

        # Assign M2M fields if provided
        if "match_pair" in validated_data:
            quiz_result.match_pair.set(validated_data["match_pair"])

        if "true_false" in validated_data:
            quiz_result.true_false.set(validated_data["true_false"])

        if "questions" in validated_data:
            quiz_result.questions.set(validated_data["questions"])

        if "cloze_test" in validated_data:
            quiz_result.cloze_test.set(validated_data["cloze_test"])

        if "objective" in validated_data:
            quiz_result.objective.set(validated_data["objective"])

        if "image_objective" in validated_data:
            quiz_result.image_objective.set(validated_data["image_objective"])

        if "vocabulary" in validated_data:
            quiz_result.vocabulary.set(validated_data["vocabulary"])

        return quiz_result


    def get_standard(self, obj):
        # Replace with actual logic and serializer
        return QuestionSerializer(obj.questions.all(), many=True).data

    def get_match_pairs(self, obj):
        return MatchPairsSerializer(obj.match_pair.all(), many=True).data

    def get_true_false(self, obj):
        return True_FalseSerializer(obj.true_false.all(), many=True).data

    def get_vocabulary(self, obj):
        return VocabularySerializer(obj.vocabulary.all(), many=True).data

    def get_objective_test(self, obj):
        return ObjectiveTestSerializer(obj.objective.all(), many=True).data

    def get_cloze_test(self, obj):
        return Cloze_TestSerializer(obj.cloze_test.all(), many=True).data

    def get_image_objective(self, obj):
        return ImageObjectiveTestSerializer(obj.image_objective.all(), many=True).data
