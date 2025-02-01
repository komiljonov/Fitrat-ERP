from rest_framework import serializers

from data.parents.models import Parent


class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = [
            'id',
            'fathers_name',
            'fathers_phone',
            'mothers_name',
            'mothers_phone',
            'lid',
            'student',
        ]