from django.shortcuts import aget_object_or_404, get_object_or_404
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
            "date",
            "created_at",
        ]

    def update(self, instance, validated_data):
        if instance.check_in and instance.check_out:
            attendance = get_object_or_404(
                Employee_attendance,
                employee=instance.employee,
                check_in=instance.check_in
            )
            attendance.check_out = instance.check_out
            attendance.save()

        return instance

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