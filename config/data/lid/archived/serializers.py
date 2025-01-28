from rest_framework import serializers

from .models import Archived
from ..new_lid.models import Lid
from ..new_lid.serializers import LidSerializer
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...student.student.models import Student
from ...student.student.serializers import StudentSerializer


class ArchivedSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(),allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(),allow_null=True)
    class Meta:
        model = Archived
        fields = [
            'id',
            'creator',
            'lid',
            'student',
            "reason",
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['creator'] = request.user
        return super().create(validated_data)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['creator'] = UserSerializer(instance.creator).data
        representation['lid'] = LidSerializer(instance.lid).data
        representation['student'] = StudentSerializer(instance.student).data

        return representation


