from rest_framework import serializers

from .models import StudentGroup
from ..groups.models import Group
from ..groups.serializers import GroupSerializer


class StudentsGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = StudentGroup
        fields = [
            'id',
            'group',
            'lead',
            'student',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['group'] = GroupSerializer(instance.group).data
        return rep
