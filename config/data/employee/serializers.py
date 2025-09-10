from rest_framework import serializers

from data.employee.models import Employee, EmployeeTransaction
from data.upload.serializers import FileUploadSerializer


class EmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee

        fields = [
            "id",
            "phone",
            "full_name",
            "first_name",
            "calculate_penalties",
            "calculate_bonus",
            "last_name",
            "role",
            "balance",
            "monitoring",
            "salary",
            "files",
            "is_archived",
            "extra_number",
            "is_call_center",
            "photo",
            "filial",
            "created_at",
        ]

    def __init__(self, *args, **kwargs):
        fields_to_remove: list | None = kwargs.pop("remove_fields", None)
        include_only: list | None = kwargs.pop("include_only", None)

        if fields_to_remove and include_only:
            raise ValueError(
                "You cannot use 'remove_fields' and 'include_only' at the same time."
            )

        super(EmployeeSerializer, self).__init__(*args, **kwargs)

        if include_only is not None:
            allowed = set(include_only)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

        elif fields_to_remove:
            for field_name in fields_to_remove:
                self.fields.pop(field_name, None)

    def to_representation(self, instance: Employee):
        rep = super().to_representation(instance)

        if "photo" in rep:
            rep["photo"] = (
                FileUploadSerializer(instance.photo, context=self.context).data
                if instance.photo
                else None
            )

        if "files" in rep:
            rep["files"] = FileUploadSerializer(
                instance.files.all(),
                many=True,
                context=self.context,
            ).data

        return rep


class EmployeeTransactionSerializer(serializers.ModelSerializer):

    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    class Meta:
        model = EmployeeTransaction
        fields = ["id", "employee", "reason", "amount", "effective_amount"]

        read_only_fields = ["effective_amount"]

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res["employee"] = EmployeeSerializer(
            instance.employee, include_only=["id", "full_name"]
        ).data

        return res
