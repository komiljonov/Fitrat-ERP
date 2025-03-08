from rest_framework import serializers

from data.account.models import CustomUser

from .models import Employee_attendance
from ...account.serializers import UserSerializer


class TimeTrackerSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(),allow_null=True)
    class Meta:
        model = Employee_attendance
        fields = [
            "id",
            "user",
            "action",
            "type",
            "date",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserSerializer(instance.user).data
        return rep
