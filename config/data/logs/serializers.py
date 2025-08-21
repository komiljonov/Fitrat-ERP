
from rest_framework import serializers

from .models import Log
from ..account.models import CustomUser
from ..finances.finance.models import Finance
from ..finances.finance.serializers import FinanceSerializer
from ..lid.archived.models import Archived
from ..lid.new_lid.models import Lid
from ..student.student.models import Student


class LogSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    account = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    finance = serializers.PrimaryKeyRelatedField(queryset=Finance.objects.all(), allow_null=True)
    archive = serializers.PrimaryKeyRelatedField(queryset=Archived.objects.all(), allow_null=True)

    class Meta:
        model = Log
        fields = [
            "id",
            "app",
            "model",
            "action",
            "model_action",
            "finance",
            "lid",
            "first_lessons",
            "student",
            "archive",
            "account",
            "comment",
            "created_at"
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["student"] = {
            "id": instance.student.id,
            "full_name": f"{instance.student.first_name} {instance.student.last_name}",
            "balance": f"{instance.student.balance}",
            "phone": f"{instance.student.phone}",
        }
        rep["lid"] = {
            "id": instance.lid.id,
            "full_name": f"{instance.lid.first_name} {instance.lid.last_name}",
            "balance": f"{instance.lid.balance}",
            "phone": f"{instance.lid.phone_number}",
        }
        rep["account"] = {
            "id": instance.account.id,
            "full_name": instance.account.full_name,
            "balance": f"{instance.account.balance}",
            "phone": f"{instance.account.phone}",
        }
        rep["finance"] = FinanceSerializer(instance.finance).data

        return rep