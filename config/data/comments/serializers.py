from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Comment
from ..account.serializers import UserSerializer

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "creator",
            "lid",
            "student",
            "comment",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        # Serialize `creator` field using UserSerializer
        representation['creator'] = UserSerializer(instance.creator).data if instance.creator else None

        return representation
