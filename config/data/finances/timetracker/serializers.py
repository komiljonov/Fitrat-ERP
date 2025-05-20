from django.shortcuts import aget_object_or_404, get_object_or_404
from icecream import ic
from rest_framework import serializers

from data.account.models import CustomUser

from .models import Employee_attendance, UserTimeLine
from ...account.serializers import UserSerializer


class TimeTrackerSerializer(serializers.ModelSerializer):
    # Bind employee via second_user field
    employee = serializers.SlugRelatedField(
        queryset=CustomUser.objects.all(),
        slug_field="second_user",
        allow_null=True
    )

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

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["employee"] = {
            "id": instance.employee.id if instance.employee else None,
            "full_name": instance.employee.full_name if instance.employee else None,
            "second_user": instance.employee.second_user if instance.employee else None,
        }
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