from .models import MarketingChannel, Group_Type
from rest_framework import serializers
from ...command.models import BaseModel

class MarketingChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingChannel
        fields = '__all__'


class Group_typeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group_Type
        fields = [
            "id",
            "price_type",
            "created_at",
            "updated_at",
        ]