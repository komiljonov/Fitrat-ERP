from rest_framework import serializers

from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LeadSerializer
from data.student.groups.models import Group
from data.student.groups.serializers import GroupSerializer
from data.student.lesson.models import FirstLLesson


class FirstLessonSerializer(serializers.ModelSerializer):

    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = FirstLLesson
        fields = ["id", "lid", "group", "date", "time", "comment", "creator"]

    def to_representation(self, instance: FirstLLesson):
        res = super().to_representation(instance)

        res["lead"] = (
            LeadSerializer(
                instance.lid,
                include_only=[
                    "id",
                    "name",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone_number",
                    "balance",
                    "sales_manager",
                ],
            ).data
            if instance.lid
            else None
        )

        res["group"] = (
            GroupSerializer(instance.group, include_only=["id", "name"]).data
            if instance.group
            else None
        )

        return res
