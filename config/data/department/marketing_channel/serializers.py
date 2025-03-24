from .models import MarketingChannel
from rest_framework import serializers
from ...command.models import BaseModel

class MarketingChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingChannel
        fields = '__all__'
