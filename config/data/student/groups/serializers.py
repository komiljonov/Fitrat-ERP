from rest_framework import serializers
from typing import TYPE_CHECKING
from .models import Group



class GroupSerializer(serializers.ModelSerializer):
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

