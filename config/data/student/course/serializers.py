from django.db.models import Count
from icecream import ic
from rest_framework import serializers

from data.student.course.models import Course
from data.student.subject.models import Level, Theme, Subject
from data.student.subject.serializers import (
    SubjectSerializer,
    ThemeSerializer,
    LevelSerializer,
)


class CourseSerializer(serializers.ModelSerializer):

    level = serializers.PrimaryKeyRelatedField(
        queryset=Level.objects.all(),
        allow_null=True,
    )

    theme = serializers.PrimaryKeyRelatedField(
        queryset=Theme.objects.all(),
        many=True,
        required=False,
        allow_null=True,
    )

    subject = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(),
        allow_null=True,
    )

    lessons_number = serializers.SerializerMethodField()

    level_counts = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            "id",
            "name",
            "level",
            "filial",
            "lessons_number",
            "level_counts",
            "theme",
            "subject",
            "status",
            "is_archived",
        ]

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(CourseSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    def to_internal_value(self, data):
        res = super().to_internal_value(data)
        res["theme"] = res.get("theme", [])
        return res

    def get_level_counts(self, obj):
        return Level.objects.filter(courses=obj, is_archived=False).count()

    def get_lessons_number(self, obj: Course):
        # return Course.objects.filter(id=obj.id).aggregate(total_lessons=Count("theme"))[
        #     "total_lessons"
        # ]
        return obj.theme.count()

    def validate_theme(self, value):
        """Allow theme to be an empty list or a list of valid theme UUIDs"""
        if value is None:
            return []  # Convert None to an empty list
        if not isinstance(value, list):
            raise serializers.ValidationError("Theme must be a list or None.")
        return value

    def create(self, validated_data):
        themes = validated_data.pop("theme", [])
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )

        course = Course.objects.create(filial=filial, **validated_data)

        if themes:
            course.theme.set(themes)

        return course

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if "subject" in self.fields:
            rep["subject"] = SubjectSerializer(
                instance.subject, context=self.context
            ).data

        # if instance.level:
        if "level" in self.fields:
            rep["level"] = (
                LevelSerializer(instance.level, context=self.context).data
                if instance.level
                else None
            )

        if "theme" in self.fields:
            rep["theme"] = ThemeSerializer(
                instance.theme.all(), many=True, context=self.context
            ).data  # Return full theme data

        return rep

    @classmethod
    def mininal(cls, *args, **kwargs):
        return cls(*args, include_only=["id", "name"], **kwargs)
