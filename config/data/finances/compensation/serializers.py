from rest_framework import serializers

from .models import Bonus, Compensation

class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = [
            'id',
            'name',
            'amount',
        ]


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = [
            'id',
            'name',
            'amount',
        ]

class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = [
            'id',
            'name',
        ]