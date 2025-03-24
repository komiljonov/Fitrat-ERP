from datetime import timedelta
from typing import TYPE_CHECKING

from aiogram.types import User
from django.db.models import Avg
from rest_framework import serializers

from .models import Bonus, Compensation, Asos, Monitoring, Page, Point, ResultSubjects, StudentCountMonitoring, \
    StudentCatchingMonitoring, ResultName, MonitoringAsos4
from ...account.models import CustomUser
from ...account.serializers import UserListSerializer

if TYPE_CHECKING:
    pass


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
    user_avg_ball = serializers.FloatField(read_only=True)  # Already annotated in queryset

    class Meta:
        model = Point
        fields = [
            'id', 'name', 'asos', "filial", 'max_ball',"amount",
            "average_point", "monitoring", "user_avg_ball",
            "created_at", "updated_at"
        ]

    def get_average_point(self, obj):
        """
        Calculates the average ball per user for the given Point within its created month.
        """
        start_of_month = obj.created_at.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = start_of_month + timedelta(days=32)
        end_of_month = next_month.replace(day=1) - timedelta(seconds=1)  # Last second of the month

        monitoring_qs = Monitoring.objects.filter(
            point=obj,
            created_at__gte=start_of_month,
            created_at__lte=end_of_month
        ).values("user").annotate(
            avg_ball=Avg("ball")
        )

        return {str(entry["user"]): entry["avg_ball"] for entry in monitoring_qs}

    def get_monitoring(self, obj):
        """
        Retrieves all monitoring records for the given Point within its created month.
        Groups by user and calculates the user's average ball.
        """
        user_monitorings = getattr(obj, "user_monitorings", [])
        return [
            {"id": mon.id,"user":mon.user.full_name ,
             "ball": mon.ball, "created_at": mon.created_at}
            for mon in user_monitorings
        ]


class ResultPointsSerializer(serializers.ModelSerializer):
    asos = serializers.PrimaryKeyRelatedField(queryset=Asos.objects.all(),allow_null=True)
    class Meta:
        model = ResultSubjects
        fields = [
            "id",
            "asos",
            "result",
            "name",
            "result_type",
            "point",
            "max_ball",

            "from_point",
            "to_point",

            "amount",
            "created_at",
            "updated_at"
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["asos"] = AsosSerializer(instance.asos).data
        return data


class StudentCountMonitoringSerializer(serializers.ModelSerializer):
    asos = serializers.PrimaryKeyRelatedField(queryset=Asos.objects.all(),allow_null=True)
    class Meta:
        model = StudentCountMonitoring
        fields = [
            "id",
            "asos",
            "max_ball",
            "amount",
            "from_point",
            "to_point",
            "created_at",
            "updated_at"
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["asos"] = AsosSerializer(instance.asos).data
        return data


class ResultsNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultName
        fields = [
            "id",
            "name",
            "point_type",
            "type",
        ]


class MonitoringAsos4Serializer(serializers.ModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),allow_null=True)
    asos = serializers.PrimaryKeyRelatedField(queryset=Asos.objects.all(),allow_null=True)
    result = serializers.PrimaryKeyRelatedField(queryset=ResultName.objects.all(),allow_null=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=ResultSubjects.objects.all(),allow_null=True)
    class Meta:
        model = MonitoringAsos4
        fields = [
            "id",
            "user",
            "asos",
            "result",
            "subject",
            "ball",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["asos"] = AsosSerializer(instance.asos).data
        data["result"] = ResultsNameSerializer(instance.result).data
        data["subject"] = ResultPointsSerializer(instance.subject).data
        data["user"] = UserListSerializer(instance.user).data
        return data


class StudentCatchupSerializer(serializers.ModelSerializer):
    asos = serializers.PrimaryKeyRelatedField(queryset=Asos.objects.all(),allow_null=True)
    class Meta:
        model = StudentCatchingMonitoring
        fields = [
            "id",
            "name",
            "asos",
            "from_student",
            "to_student",
            "type",
            "ball",
            "created_at",
        ]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["asos"] = AsosSerializer(instance.asos).data
        return data