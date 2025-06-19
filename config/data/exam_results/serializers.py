
from rest_framework import serializers

from .models import UnitTest, UnitTestResult, QuizResult
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
    class Meta:
        model = QuizResult
        fields = [
            "id",
            "student",
            "questions",
            "match_pair",
            "true_false",
            "vocabulary",
            "objective",
            "cloze_test",
            "image_objective",
            "point",
            "created_at"
        ]