
from .models import Log
from rest_framework import serializers


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = [
            "id",
            "app",
            "model",
            "action",
            "model_action",
            "finance",
            "lid",
            "first_lessons",
            "student",
            "archive",
            "account",
            "created_at"
        ]