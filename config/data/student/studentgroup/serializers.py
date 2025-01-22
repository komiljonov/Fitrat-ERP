from .models import StudentGroup

from rest_framework import serializers

from ..groups.models import Group
from ..groups.serializers import GroupSerializer
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class StudentGroupSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    lead  = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())


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
        rep['lead'] = LidSerializer(instance.lead).data
        rep['student'] = StudentSerializer(instance.student).data
        return rep
