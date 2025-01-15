
from rest_framework import serializers

from .models import Moderator


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = [
            'id',
            'full_name',
            'phone',
            'photo',
            'role',
            'created_at',
            'updated_at',
            'balance',
        ]
