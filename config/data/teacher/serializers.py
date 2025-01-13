
from rest_framework import serializers

from ..teacher.models import Teacher

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
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


