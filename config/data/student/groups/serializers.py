from rest_framework import serializers
from typing import TYPE_CHECKING
from .models import Group, StudentGroup
if TYPE_CHECKING:

    from ..student.serializers import StudentSerializer


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'price_type',
            'price',
            'scheduled_day_type',
            'started_at',
            'ended_at',
        ]


class StudentGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'student',
            'group',
            'student_status',
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['student'] = StudentSerializer(instance.student).data if instance.student else None
        representation['group'] = GroupSerializer(instance.group).data if instance.group else None
        return representation