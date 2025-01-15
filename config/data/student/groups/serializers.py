from rest_framework import serializers
from .models import Group
from ...account.models import CustomUser
from ...account.serializers import UserSerializer


class GroupSerializer(serializers.ModelSerializer):
    teacher = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Group
        fields = [
            'id',
            'name',
            'teacher',
            'price_type',
            'price',
            'scheduled_day_type',
            'started_at',
            'ended_at',
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['teacher'] = UserSerializer(instance.teacher).data
        return rep
