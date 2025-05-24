from rest_framework import serializers

from data.account.models import CustomUser

from .models import Employee_attendance, UserTimeLine
from ...account.serializers import UserSerializer


class TimeTrackerSerializer(serializers.ModelSerializer):
    employee = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),
                                              allow_null=True)
    class Meta:
        model = Employee_attendance
        fields = [
            "id",
            "employee",
            "check_in",
            "check_out",
            "not_marked",
            "status",
            "date",
            "amount",
            "created_at",
        ]

    def create(self, validated_data):
        employee = validated_data.get("employee")
        if employee:
            try:
                user = CustomUser.objects.get(second_user=employee)
                validated_data["employee"] = user  # not user.pk
            except CustomUser.DoesNotExist:
                raise serializers.ValidationError("No CustomUser found with the given second_user")
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["employee"] = UserSerializer(instance.employee).data
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