
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
    # Write-only fields for incoming UUID lists
    match_pair = serializers.ListField(write_only=True, required=False)
    true_false = serializers.ListField(write_only=True, required=False)
    questions = serializers.ListField(write_only=True, required=False)
    cloze_test = serializers.ListField(write_only=True, required=False)
    objective = serializers.ListField(write_only=True, required=False)
    image_objective = serializers.ListField(write_only=True, required=False)
    vocabulary = serializers.ListField(write_only=True, required=False)

    # Read-only output fields
    standard = serializers.SerializerMethodField()
    match_pair_result = serializers.SerializerMethodField()
    true_false_result = serializers.SerializerMethodField()
    vocabulary_result = serializers.SerializerMethodField()
    objective_result = serializers.SerializerMethodField()
    cloze_test_result = serializers.SerializerMethodField()
    image_objective_result = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = [
            "id", "student", "point", "created_at", "quiz",
            "questions", "match_pair", "true_false", "vocabulary",
            "objective", "cloze_test", "image_objective",
            "standard", "match_pair_result", "true_false_result",
            "vocabulary_result", "objective_result",
            "cloze_test_result", "image_objective_result"
        ]

    def create(self, validated_data):
        request = self.context.get("request")
        student = validated_data.get("student")

        print("student",student)

        if not student and request and hasattr(request.user, 'student'):
            student = Student.objects.filter(user=request.user).first()

            print("finded",student)

        quiz = validated_data["quiz"]
        quiz_result = QuizResult.objects.create(student=student, quiz=quiz)

        # Assign M2M fields if provided
        m2m_fields = [
            ("match_pair", "match_pair"),
            ("true_false", "true_false"),
            ("questions", "questions"),
            ("cloze_test", "cloze_test"),
            ("objective", "objective"),
            ("image_objective", "image_objective"),
            ("vocabulary", "vocabulary"),
        ]
        for key, attr in m2m_fields:
            if key in validated_data:
                getattr(quiz_result, attr).set(validated_data[key])

        return quiz_result

    # Read methods for result representation
    def get_standard(self, obj):
        return QuestionSerializer(obj.questions.all(), many=True).data

    def get_match_pair_result(self, obj):
        return MatchPairsSerializer(obj.match_pair.all(), many=True).data

    def get_true_false_result(self, obj):
        return True_FalseSerializer(obj.true_false.all(), many=True).data

    def get_vocabulary_result(self, obj):
        return VocabularySerializer(obj.vocabulary.all(), many=True).data

    def get_objective_result(self, obj):
        return ObjectiveTestSerializer(obj.objective.all(), many=True).data

    def get_cloze_test_result(self, obj):
        return Cloze_TestSerializer(obj.cloze_test.all(), many=True).data

    def get_image_objective_result(self, obj):
        return ImageObjectiveTestSerializer(obj.image_objective.all(), many=True).data

