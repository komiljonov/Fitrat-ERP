from rest_framework import serializers

from .models import Archived
from ...account.serializers import UserSerializer


class ArchivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Archived
        fields = [
            'id',
            'creator',
            "reason"
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['creator'] = request.user
        return super().create(validated_data)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['creator'] = UserSerializer(instance.creator).data
        return representation


