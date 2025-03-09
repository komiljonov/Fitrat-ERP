from rest_framework import serializers

from .models import Bonus, Compensation, Page, Asos, Monitoring
from ...account.serializers import UserSerializer


class BonusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bonus
        fields = ['id', 'name', 'user', 'amount']

    def create(self, validated_data):
        if isinstance(validated_data, list):
            return Bonus.objects.bulk_create([Bonus(**data) for data in validated_data])
        return super().create(validated_data)


class CompensationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compensation
        fields = ['id', 'name', 'user', 'amount']

    def create(self, validated_data):
        if isinstance(validated_data, list):
            return Compensation.objects.bulk_create([Compensation(**data) for data in validated_data])
        return super().create(validated_data)

from rest_framework import serializers
from .models import Page

class PagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ['id', 'name', 'user', 'is_editable', 'is_readable', 'is_parent']

    def create(self, validated_data):
        if isinstance(validated_data, list):
            return Page.objects.bulk_create([Page(**data) for data in validated_data])
        return super().create(validated_data)


class AsosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asos
        fields = ['id', 'name', 'max_ball']


class MonitoringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitoring
        fields = [
            "id",
            "user",
            "asos",
            "ball",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep["user"] = UserSerializer(instance.user).data
        rep["asos"] = AsosSerializer(instance.asos).data

        return rep

