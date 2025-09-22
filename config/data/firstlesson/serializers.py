from datetime import date as _date

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from data.firstlesson.models import FirstLesson
from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LeadSerializer
from data.student.groups.models import Group


class FirstLessonListSerializer(serializers.ModelSerializer):
    lead = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.filter(status="ACTIVE")
    )

    class Meta:
        model = FirstLesson
        fields = [
            "id",
            "lead",
            "group",
            "teacher",
            "subject",
            "level",
            "course",
            "date",
            "status",
            "comment",
            "creator",
            "created_at",
        ]

        read_only_fields = [
            "status",
            "creator",
            "teacher",
            "subject",
            "level",
            "course",
        ]

    def validate(self, attrs):

        lead: "Lid" = attrs["lead"]
        group: "Group" = attrs["group"]
        date: _date = attrs["date"]

        if lead.relatives.count() == 0:
            raise ValidationError(
                "O'quvchining kamida 1 ta qarindoshi bo'lishi kerak.",
                "relatives_not_found",
            )

        if group.scheduled_day_type.filter(index=date.weekday()).count() == 0:
            raise ValidationError("Guruhda bu kunga darslar yo'q.", "no_lesson_date")

        return attrs

    def _apply_group_defaults(self, validated_data):
        group = validated_data.get("group")
        if group:
            validated_data["teacher"] = getattr(group, "teacher", None)
            validated_data["subject"] = getattr(group, "subject", None)
            validated_data["level"] = getattr(group, "level", None)
            validated_data["course"] = getattr(group, "course", None)

    def create(self, validated_data):
        # set creator if you map users->employees
        req = self.context.get("request")
        if req and hasattr(req.user, "employee"):
            validated_data["creator"] = req.user.employee

        self._apply_group_defaults(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If group is being changed via API, re-sync derived fields for the saved object
        if "group" in validated_data:
            self._apply_group_defaults(validated_data)
        return super().update(instance, validated_data)

    def to_representation(self, instance: FirstLesson):
        res = super().to_representation(instance)

        res["lead"] = LeadSerializer(
            instance.lead,
            context=self.context,
            include_only=[
                "id",
                "first_name",
                "last_name",
                "middle_name",
                "phone_number",
                "service_manager",
                "sales_manager",
                "balance",
                "filial",
                "photo",
            ],
        ).data

        return res


class FirstLessonSingleSerializer(serializers.ModelSerializer):
    lead = LeadSerializer()
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.filter(status="ACTIVE")
    )

    class Meta:
        model = FirstLesson
        fields = [
            "id",
            "lead",
            "group",
            "teacher",
            "subject",
            "level",
            "course",
            "date",
            "status",
            "comment",
            "creator",
            "created_at",
        ]

        read_only_fields = [
            "status",
            "creator",
            "teacher",
            "subject",
            "level",
            "course",
        ]

    def _apply_group_defaults(self, validated_data):
        group = validated_data.get("group")
        if group:
            validated_data["teacher"] = getattr(group, "teacher", None)
            validated_data["subject"] = getattr(group, "subject", None)
            validated_data["level"] = getattr(group, "level", None)
            validated_data["course"] = getattr(group, "course", None)

    def create(self, validated_data):
        # set creator if you map users->employees
        req = self.context.get("request")
        if req and hasattr(req.user, "employee"):
            validated_data["creator"] = req.user.employee

        self._apply_group_defaults(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # If group is being changed via API, re-sync derived fields for the saved object
        if "group" in validated_data:
            self._apply_group_defaults(validated_data)
        return super().update(instance, validated_data)
