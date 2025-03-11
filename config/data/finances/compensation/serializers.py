from rest_framework import serializers

from .models import Bonus, Compensation, Asos, Monitoring, Page, Point

from typing import TYPE_CHECKING

from ...account.models import CustomUser

if TYPE_CHECKING:
    from ...account.serializers import UserSerializer, UserListSerializer


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
        fields = ['id', 'name',"created_at", "updated_at"]

class MonitoringSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),allow_null=True)
    point = serializers.PrimaryKeyRelatedField(queryset=Point.objects.all(),allow_null=True)
    class Meta:
        model = Monitoring
        fields = [
            "id",
            "user",
            "point",
            "ball",
            "created_at",
        ]


    def to_representation(self, instance):

        from ...account.serializers import UserListSerializer

        rep = super().to_representation(instance)

        rep["user"] = UserListSerializer(instance.user).data
        rep["point"] = PointSerializer(instance.point).data

        return rep



class PointSerializer(serializers.ModelSerializer):
    average_point = serializers.SerializerMethodField()
    monitoring = serializers.SerializerMethodField()

    class Meta:
        model = Point
        fields = ['id', 'name', 'asos', "filial", 'max_ball', "average_point", "monitoring", "created_at", "updated_at"]

    def get_average_point(self, obj):
        monitoring_qs = Monitoring.objects.filter(point__asos=obj.asos)
        points = monitoring_qs.values_list('ball', flat=True)

        if not points:
            return 0

        return sum(points) / len(points)

    def get_monitoring(self, obj):
        monitoring_qs = Monitoring.objects.filter(point=obj)
        return list(monitoring_qs.values("user",'ball',"created_at",))


