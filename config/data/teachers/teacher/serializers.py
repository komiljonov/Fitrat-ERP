
from rest_framework import serializers

from ...account.models import CustomUser


class TeacherSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'full_name',
            'phone',
            'photo',
            'role',
            'balance',
            'created_at',
            'updated_at',
        ]





