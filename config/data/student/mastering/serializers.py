from rest_framework import serializers

from .models import Mastering, MasteringTeachers
from ..quiz.models import Quiz
from ..quiz.serializers import QuizSerializer


class MasteringSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    class Meta:
        model = Mastering
        fields = [
            "id",
            "lid",
            "student",
            "test",
            "ball",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["test"] = QuizSerializer(instance.test).data
        return rep


class StuffMasteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasteringTeachers
        fields = [
            "id",
            "teacher",
            "ball",
            'reason',
            'created_at',
            'updated_at',
        ]

