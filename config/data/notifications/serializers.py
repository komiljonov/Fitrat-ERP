from rest_framework import serializers

from .models import Notification, UserRFToken
from ..account.models import CustomUser
from ..account.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'comment',
            'come_from',
            "choice",
            'is_read',
            'has_read',
            'created_at',
            'updated_at',
        ]

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #
    #     rep['user'] = UserSerializer(instance.user).data
    #
    #     return rep


class UserRFTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRFToken
        fields = [
            'id',
            'user',
            'token',
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['user'] = UserSerializer(instance.user).data
        return ret