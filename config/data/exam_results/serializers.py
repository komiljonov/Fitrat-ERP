
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
    standard = serializers.SerializerMethodField()
    match_pairs = serializers.SerializerMethodField()
    true_false = serializers.SerializerMethodField()
    vocabulary = serializers.SerializerMethodField()
    objective_test = serializers.SerializerMethodField()
    cloze_test = serializers.SerializerMethodField()
    image_objective = serializers.SerializerMethodField()

    class Meta:
        model = QuizResult
        fields = [
            "id", "student", "point", "created_at","quiz",
            "standard", "match_pairs", "true_false", "vocabulary",
            "objective_test", "cloze_test", "image_objective"
        ]

    def create(self, validated_data):

        print(validated_data)
        if not validated_data.get("student"):
            request = self.context.get("request")
            if request and hasattr(request.user, 'student'):
                validated_data["student"] = Student.objects.filter(user=request.user).first()
        return QuizResult.objects.create(**validated_data)

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
