from rest_framework import serializers

from .models import Log
from data.account.models import CustomUser
from data.finances.finance.models import Finance
from data.finances.finance.serializers import FinanceSerializer
from data.lid.archived.models import Archived
from data.lid.new_lid.models import Lid
from data.student.student.models import Student


class LogSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
    )
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
    )
    account = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        allow_null=True,
    )
    finance = serializers.PrimaryKeyRelatedField(
        queryset=Finance.objects.all(),
        allow_null=True,
    )
    archive = serializers.PrimaryKeyRelatedField(
        queryset=Archived.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = Log
        fields = [
            "id",
            # "app",
            # "model",
            "action",
            # "model_action",
            "finance",
            "lead",
            "first_lessons",
            "student",
            "archive",
            "account",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance: Log):
        rep = super().to_representation(instance)
        rep["student"] = (
            {
                "id": instance.student.id,
                "full_name": f"{instance.student.first_name} {instance.student.last_name}",
                "balance": f"{instance.student.balance}",
                "phone": f"{instance.student.phone}",
            }
            if instance.student
            else {}
        )
        rep["lead"] = (
            {
                "id": instance.lead.id,
                "full_name": f"{instance.lead.first_name} {instance.lead.last_name}",
                "balance": f"{instance.lead.balance}",
                "phone": f"{instance.lead.phone_number}",
            }
            if instance.lead
            else {}
        )
        rep["account"] = (
            {
                "id": instance.account.id,
                "full_name": instance.account.full_name,
                "balance": f"{instance.account.balance}",
                "phone": f"{instance.account.phone}",
            }
            if instance.account
            else {}
        )
        rep["finance"] = FinanceSerializer(instance.finance).data

        return rep
