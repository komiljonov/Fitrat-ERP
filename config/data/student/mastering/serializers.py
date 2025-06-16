from icecream import ic
from rest_framework import serializers

from .models import Mastering, MasteringTeachers
from ..quiz.models import Quiz
from ..quiz.serializers import QuizSerializer
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer


class MasteringSerializer(serializers.ModelSerializer):
    test = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(),allow_null=True)
    class Meta:
        model = Mastering
        fields = [
            "id",
            "lid",
            "student",
            "test",
            "choice",
            "theme",
            "ball",
            "created_at",
        ]
    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        theme = validated_data.pop("theme", None)

        ic(theme)

        if not theme:
            theme = None
            validated_data["theme"] = theme

        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = Mastering.objects.create(filial=filial, **validated_data)
        return room

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["test"] = QuizSerializer(instance.test).data
        rep["theme"] = ThemeSerializer(instance.theme).data
        return rep


class StuffMasteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasteringTeachers
        fields = [
            "id",
            "teacher",
            "ball",
            "bonus",
            'reason',
            'created_at',
            'updated_at',
        ]
    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError({"filial": "Filial could not be determined."})

        room = MasteringTeachers.objects.create(filial=filial, **validated_data)
        return room

