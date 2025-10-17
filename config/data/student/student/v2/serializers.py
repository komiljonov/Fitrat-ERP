from data.student.student.models import StudentFrozenAction
from rest_framework import serializers
from django.utils import timezone


class StudentFrozenActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentFrozenAction
        fields = ["id", "student", "from_date", "till_date", "reason", "created_at"]
        read_only_fields = ["id", "student", "created_at"]

    def validate(self, data):
        today = timezone.now().date()
        print(data)
        if  today > data["till_date"]:
            raise serializers.ValidationError("from_date cannot be after till_date.")
        return data