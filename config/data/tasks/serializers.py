from django.contrib.auth import get_user_model
from rest_framework import serializers

from ..tasks.models import Task
from ..account.serializers import UserListSerializer

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Task
        fields = [
            "id",
            "creator",
            "task",
            "comment",
            "date_of_expired",
            "status",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['creator'] = request.user
        return super().create(validated_data)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Corrected the syntax for `UserListSerializer`
        representation["creator"] = UserListSerializer(instance.creator).data
        return representation
