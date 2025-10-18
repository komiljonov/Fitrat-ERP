from rest_framework import serializers
from data.employee.serializers import EmployeeSerializer
from data.lid.new_lid.serializers import LeadSerializer
from data.student.student.serializers import StudentSerializer
from data.student.student.models import Student
from data.lid.new_lid.models import Lid
from data.employee.models import Employee
from .models import StudentTransaction


class StudentTransactionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True, required=False
    )
    lead = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(), allow_null=True, required=False
    )
    created_by = EmployeeSerializer(read_only=True)

    # Read-only fields that are calculated
    effective_amount = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )

    class Meta:
        model = StudentTransaction
        fields = [
            "id",
            "reason",
            "action",
            "student",
            "lead",
            "amount",
            "effective_amount",
            "comment",
            "created_by",
            "created_at",
            "updated_at",
            "is_archived",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "is_archived", "action", "created_by"]

    def validate(self, attrs):
        student = attrs.get("student")
        lead = attrs.get("lead")
        reason = attrs.get("reason")

        if not reason:
            raise serializers.ValidationError("Reason should be provided.")

        if not student and not lead:
            raise serializers.ValidationError(
                "Either 'student' or 'lead' must be provided."
            )

        return attrs

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res["student"] = (
            StudentSerializer(
                instance.student, include_only=["id", "first_name", "last_name"]
            ).data
            if instance.student
            else None
        )

        res["lead"] = (
            LeadSerializer(
                instance.lead, include_only=["id", "first_name", "last_name"]
            ).data
            if instance.lead
            else None
        )

        res["created_by"] = (
            EmployeeSerializer(
                instance.created_by, include_only=["id", "full_name"]
            ).data
            if instance.created_by
            else None
        )

        return res