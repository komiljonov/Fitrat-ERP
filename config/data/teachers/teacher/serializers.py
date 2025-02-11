
from rest_framework import serializers

from ...account.models import CustomUser
from ...student.studentgroup.models import StudentGroup, SecondaryStudentGroup
from ...student.studentgroup.serializers import StudentGroupMixSerializer, SecondaryStudentsGroupSerializer


class TeacherSerializer(serializers.ModelSerializer):

    groups = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'full_name',
            'phone',
            'photo',
            'role',
            'groups',
            'balance',
            'created_at',
            'updated_at',
        ]
    def get_groups(self, obj):
        groups = StudentGroup.objects.filter(group__teacher=obj)
        return StudentGroupMixSerializer(groups, many=True).data



class AssistantSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'full_name',
            'phone',
            'photo',
            'role',
            'groups',
            'balance',
            'created_at',
            'updated_at',
        ]

    def get_groups(self, obj):
        groups = SecondaryStudentGroup.objects.filter(group__teacher=obj)
        return SecondaryStudentsGroupSerializer(groups, many=True).data
