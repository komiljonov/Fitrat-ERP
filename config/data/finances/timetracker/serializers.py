from icecream import ic
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from data.account.models import CustomUser

from .models import Employee_attendance, UserTimeLine
from ...account.serializers import UserSerializer


class TimeTrackerSerializer(serializers.ModelSerializer):
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

    # def create(self, validated_data):
    #     print("All validated data:", validated_data)
    #     external_user_id = validated_data.get("employee")
    #     print(f"Employee value: '{external_user_id}', type: {type(external_user_id)}")
    #     if external_user_id:
    #         user = CustomUser.objects.get(second_user=external_user_id)
    #         validated_data["employee"] = user
    #
    #     return super().create(validated_data)


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
