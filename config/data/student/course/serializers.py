from rest_framework import serializers

from data.student.course.models import Course
from data.student.subject.models import Level, Theme
from data.student.subject.serializers import SubjectSerializer, ThemeSerializer, LevelSerializer

class CourseSerializer(serializers.ModelSerializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    theme = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(), many=True, required=False, allow_null=True
    )

    class Meta:
        model = Course
        fields = ["id", "name", "level", "lessons_number", "theme", "subject", "status"]

    def to_internal_value(self, data):
        res = super().to_internal_value(data)
        res["theme"] = res.get("theme", [])
        return res

    def validate_theme(self, value):
        """Allow theme to be an empty list or a list of valid theme UUIDs"""
        if value is None:
            return []  # Convert None to an empty list
        if not isinstance(value, list):
            raise serializers.ValidationError("Theme must be a list or None.")
        return value

    def create(self, validated_data):
        themes = validated_data.pop("theme", [])  # Extract theme IDs (or empty list)
        course = Course.objects.create(**validated_data)  # Create Course instance
        if themes:  # Only set themes if the list is not empty
            course.theme.set(themes)
        return course

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["level"] = LevelSerializer(instance.level).data
        rep["theme"] = ThemeSerializer(instance.theme.all(), many=True).data  # Return full theme data
        return rep
