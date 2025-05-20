from rest_framework import serializers

from data.account.models import CustomUser

from .models import Employee_attendance, UserTimeLine
from ...account.serializers import UserSerializer


class TimeTrackerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                              allow_null=True)
    class Meta:
        model = Employee_attendance
        fields = [
            "id",
            "user",
            "check_in",
            "check_out",
            "not_marked",
            "date",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserSerializer(instance.user).data
        return rep


class UserTimeLineSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),allow_null=True
    )
    class Meta:
        model = UserTimeLine
        fields = [
            "id",
            "user",
            "day",
            "start_time",
            "end_time",
            "created_at",
        ]