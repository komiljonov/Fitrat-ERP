from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..account.models import CustomUser
from ..lid.new_lid.models import Lid
from ..student.student.models import Student
from ..tasks.models import Task
from ..account.serializers import UserListSerializer



class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    class Meta:
        model = Task
        fields = [
            "id",
            "creator",
            'lid',
            'student',
            "task",
            "comment",
            "date_of_expired",
            "status",
            "created_at",
            "updated_at",
        ]


    def to_internal_value(self, data):

        data['creator'] = self.context['request'].user.id

        return super(TaskSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        request = self.context['request']
        validated_data['creator'] = request.user
        return super().create(validated_data)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Corrected the syntax for `UserListSerializer`
        representation["creator"] = UserListSerializer(instance.creator).data
        return representation
