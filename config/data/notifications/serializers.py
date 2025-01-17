from rest_framework import serializers

from .models import Notification
from ..account.models import CustomUser
from ..account.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'comment',
            'come_from',
            'is_read',
            'created_at',
            'updated_at',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep['user'] = UserSerializer(instance.user).data

        return rep