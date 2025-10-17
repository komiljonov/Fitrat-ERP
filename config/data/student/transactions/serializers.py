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
    created_by = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        allow_null=True,
        required=False,
        write_only=True,
    )

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
        read_only_fields = ["id", "created_at", "updated_at", "is_archived", "action"]

    def validate(self, attrs):
        # Ensure either student or lead is provided, but not both
        student = attrs.get("student")
        lead = attrs.get("lead")
        reason = attrs.get("reason")

        if not reason:
            raise serializers.ValidationError("Reason should be provided.")

        if not student and not lead:
            raise serializers.ValidationError(
                "Either 'student' or 'lead' must be provided."
            )

        # Set the action based on reason if not provided
        action = StudentTransaction.REASON_TO_ACTION.get(reason)
        if action:
            attrs["action"] = action

        return attrs

    def create(self, validated_data):
        # Set created_by from request user if not provided
        request = self.context.get("request")
        if request and request.user and hasattr(request.user, "employee"):
            validated_data["created_by"] = request.user.employee

        return super().create(validated_data)

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


class StudentTransactionCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating transactions"""

    class Meta:
        model = StudentTransaction
        fields = [
            "reason",
            "action",
            "student",
            "lead",
            "amount",
            "comment",
        ]

    def validate(self, attrs):
        student = attrs.get("student")
        lead = attrs.get("lead")

        if not student and not lead:
            raise serializers.ValidationError(
                "Either 'student' or 'lead' must be provided."
            )

        if student and lead:
            raise serializers.ValidationError(
                "Only one of 'student' or 'lead' can be provided, not both."
            )

        return attrs

    def create(self, validated_data):
        # Set created_by from request user
        request = self.context.get("request")
        if request and request.user and hasattr(request.user, "employee"):
            validated_data["created_by"] = request.user.employee

        return super().create(validated_data)
