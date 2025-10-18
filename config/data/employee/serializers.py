from django.db import transaction

from psycopg2.extras import NumericRange

from rest_framework import serializers

from data.lid.new_lid.models import Lid
from data.student.student.models import Student
from data.command.serializers import BaseSerializer

from data.employee.finance import FinanceManagerKpi
from data.employee.models import Employee, EmployeeTransaction
from data.finances.compensation.models import Page
from data.finances.compensation.serializers import PagesSerializer
from data.lid.new_lid.serializers import LeadSerializer
from data.student.student.serializers import StudentSerializer
from data.upload.serializers import FileUploadSerializer


class DecimalRangeFieldSerializer(serializers.Field):
    """Serializer for Django's DecimalRangeField (psycopg NumericRange)."""

    def to_representation(self, value):
        if value is None:
            return None
        return {
            "lower": value.lower,
            "upper": value.upper,
            "bounds": value._bounds,  # usually '[)' by default
        }

    def to_internal_value(self, data):
        if data is None:
            return None

        try:
            lower = data.get("lower")
            upper = data.get("upper")
            bounds = data.get("bounds", "[)")

            if lower is None or upper is None:
                raise serializers.ValidationError(
                    "Both 'lower' and 'upper' are required."
                )
            return NumericRange(lower, upper, bounds)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid range data: {e}")


class FinanceManagerKpiSerializer(serializers.ModelSerializer):

    range = DecimalRangeFieldSerializer()

    class Meta:
        model = FinanceManagerKpi
        fields = ["id", "employee", "action", "range", "amount"]

        extra_kwargs = {"id": {"required": False}, "employee": {"required": False}}


class EmployeeSerializer(BaseSerializer, serializers.ModelSerializer):

    finance_manager_kpis = FinanceManagerKpiSerializer(
        many=True,
        required=False,
        allow_empty=True,
    )

    pages = PagesSerializer(many=True, required=False)

    class Meta:
        model = Employee

        fields = [
            "id",
            "phone",
            "password",
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
            "is_service_manager",
            "photo",
            "filial",
            "created_at",
            ############################################
            ##     Finance fields bonus and fines     ##
            ############################################
            "f_op_bonus_create_order",
            "f_sm_bonus_create_first_lesson",
            "f_sm_bonus_first_lesson_come",
            "f_sm_bonus_new_active_student",
            "f_sm_fine_firstlesson_archived",
            "f_sm_fine_new_student_archived",
            "f_svm_bonus_for_each_active_student",
            "f_svm_fine_student_archived",
            "f_managers_bonus_for_each_active_student",
            "f_ht_bonus_for_each_active_student",
            "f_t_lesson_payment_percent",
            "f_t_fine_failed_first_lesson",
            "finance_manager_kpis",
            "pages",
        ]
        
        extra_kwargs = {
            "password": {"write_only": True, "required": False}
        }

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

    def _replace_kpis(self, employee: Employee, kpis_data: list[dict] | None):
        employee.finance_manager_kpis.all().delete()
        if not kpis_data:
            return
        for item in kpis_data:
            item.pop("employee", None)  # ignore if client sent it
            FinanceManagerKpi.objects.create(employee=employee, **item)

    def _replace_pages(self, employee: Employee, pages_data: list[dict] | None):
        employee.pages.all().delete()
        if not pages_data:
            return
        objs = []
        for item in pages_data:
            item.pop("user", None)  # always bind to this employee
            item.pop("id", None)  # fresh rows on replace
            objs.append(Page(user=employee, **item))

        Page.objects.bulk_create(objs)

    def create(self, validated_data):
        kpis = validated_data.pop("finance_manager_kpis", None)
        pages = validated_data.pop("pages", None)
        password = validated_data.pop("password", None)

        with transaction.atomic():
            # Use the manager's create_user method to properly hash the password
            if password:
                employee = Employee.objects.create_user(
                    password=password,
                    **validated_data
                )
            else:
                employee = super().create(validated_data)
            
            if kpis is not None:
                self._replace_kpis(employee, kpis)
            if pages is not None:
                self._replace_pages(employee, pages)
        return employee

    def update(self, instance, validated_data):
        kpis = validated_data.pop("finance_manager_kpis", None)
        pages = validated_data.pop("pages", None)
        password = validated_data.pop("password", None)
        
        with transaction.atomic():
            # Handle password update separately to ensure proper hashing
            if password:
                instance.set_password(password)
            
            instance = super().update(instance, validated_data)
            if kpis is not None:
                self._replace_kpis(instance, kpis)
            if pages is not None:
                self._replace_pages(instance, pages)
        return instance

    @classmethod
    def minimal(cls, *args, **kwargs):
        return cls(
            *args,
            include_only=[
                "id",
                "first_name",
                "last_name",
                "middle_name",
                "phone",
            ],
            **kwargs,
        )


class EmployeeTransactionSerializer(serializers.ModelSerializer):

    employee = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())

    reason_text = serializers.SerializerMethodField()

    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lead = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    class Meta:
        model = EmployeeTransaction
        fields = [
            "id",
            "employee",
            "reason",
            "reason_text",
            "action",
            "amount",
            "effective_amount",
            "comment",
            "student",
            "first_lesson_new",
            "lead",
            "finance",
        ]

        read_only_fields = ["effective_amount", "action", "student", "lead"]

    def to_representation(self, instance):
        res = super().to_representation(instance)

        res["employee"] = EmployeeSerializer(
            instance.employee, include_only=["id", "full_name"]
        ).data

        res["student"] = StudentSerializer(
            instance.employee, include_only=["id"]
        ).data

        res["lid"] = LeadSerializer(
            instance.employee, include_only=["id"]
        ).data

        return res

    def get_reason_text(self, obj: EmployeeTransaction):

        return EmployeeTransaction.REASON_TO_TEXT.get(obj.reason, obj.reason)
