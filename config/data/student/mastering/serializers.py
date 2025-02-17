from rest_framework import serializers

from .models import Mastering, MasteringTeachers
from ..quiz.models import Quiz
from ..quiz.serializers import QuizSerializer
from ...account.serializers import UserSerializer
from ...finances.compensation.serializers import CompensationSerializer, BonusSerializer


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
            "compensation",
            "bonus",
            "ball",
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.compensation:
            rep["compensation"] = CompensationSerializer(instance.compensation).data
        if instance.bonus:
            rep["bonus"] = BonusSerializer(instance.bonus).data

        filter_data = {key: value for key, value in rep.items() if value not in [{}, None, "", False]}
        return filter_data
