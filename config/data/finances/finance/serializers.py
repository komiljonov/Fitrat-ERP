from datetime import datetime, time, timedelta
from django.db.models import Sum, Count, Q, Case, When, FloatField, F, Value
from django.db.models.functions import Coalesce
from django.utils.dateparse import parse_date
from django.db import models
from django.utils import timezone

from rest_framework import serializers

from data.finances.finance.choices import FinanceKindTypeChoices
from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.student.student.models import Student

from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LeadSerializer
from data.student.attendance.models import Attendance
from data.student.groups.serializers import GroupSerializer
from data.student.student.serializers import StudentSerializer

from .models import (
    Finance,
    Casher,
    Handover,
    Kind,
    PaymentMethod,
    KpiFinance,
    Sale,
    SaleStudent,
    Voucher,
    VoucherStudent,
)


class KindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kind
        fields = [
            "id",
            "name",
            "kind",
            "action",
            "color",
            "created_at",
        ]


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            "id",
            "name",
        ]


class CasherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    balance = serializers.SerializerMethodField()
    income = serializers.SerializerMethodField()
    expense = serializers.SerializerMethodField()

    class Meta:
        model = Casher
        fields = [
            "id",
            "name",
            "user",
            "role",
            "balance",
            "income",
            "expense",
            "is_archived",
            "comment",
        ]

    def get_balance(self, obj):

        request = self.context.get("request")
        # start_date = request.GET.get("start_date")
        # end_date = request.GET.get("end_date")

        all_qs = Finance.objects.filter(casher=obj).exclude(
            # Q(kind__kind=FinanceKindTypeChoices.BONUS) | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
            Q(kind__kind=FinanceKindTypeChoices.BONUS)
            | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
        )

        balance = all_qs.aggregate(
            total=Coalesce(
                Sum(
                    Case(
                        When(action="INCOME", then=F("amount")),
                        When(action="EXPENSE", then=F("amount") * -1),
                        output_field=FloatField(),
                    )
                ),
                Value(0.0),
            )
        )["total"]

        return round(balance, 2)

    # def get_income(self, obj):
    #     request = self.context.get("request")
    #     start_date = request.GET.get("start_date")
    #     end_date = request.GET.get("end_date")

    #     income = (
    #         Finance.objects.filter(casher=obj, action="INCOME").aggregate(
    #             Sum("amount")
    #         )["amount__sum"]
    #         or 0
    #     )

    #     if start_date:
    #         start = parse_date(start_date)
    #         end = parse_date(end_date) if end_date else start

    #         end = end + timedelta(days=1) - timedelta(seconds=1)

    #         income = (
    #             Finance.objects.filter(
    #                 casher=obj,
    #                 action="INCOME",
    #                 created_at__gte=start,
    #                 created_at__lte=end,
    #             ).aggregate(Sum("amount"))["amount__sum"]
    #             or 0
    #         )

    #     if start_date and end_date:
    #         income = (
    #             Finance.objects.filter(
    #                 casher=obj,
    #                 action="INCOME",
    #                 created_at__gte=start_date,
    #                 created_at__lte=end_date,
    #             ).aggregate(Sum("amount"))["amount__sum"]
    #             or 0
    #         )

    #     return income

    def get_income(self, obj):
        # DRF Request (query_params) or plain Django (GET)
        request = self.context.get("request")
        params = (
            getattr(request, "query_params", None) or getattr(request, "GET", {}) or {}
        )

        start_str = params.get("start_date")
        end_str = params.get("end_date")

        qs = Finance.objects.filter(casher=obj, action="INCOME").exclude(
            kind__kind__in=[
                FinanceKindTypeChoices.BONUS,
                FinanceKindTypeChoices.MONEY_BACK,
            ]
        )

        # If no dates are provided → aggregate everything (already excluding unwanted kinds)
        if not start_str:
            return qs.aggregate(total=Coalesce(Sum("amount"), 0.0, output_field=models.FloatField))["total"]

        # Parse dates (YYYY-MM-DD); fall back to start if end missing/invalid
        start_date = parse_date(start_str)
        end_date = parse_date(end_str) if end_str else start_date
        if not start_date:
            # If start_date is invalid, treat as 0 (or raise, depending on your API design)
            return 0

        # Inclusive end of day using half-open interval [start_dt, end_next_dt)
        # This avoids edge cases with seconds/microseconds and uses indexes on DateTimeField.
        tz = timezone.get_current_timezone()
        start_dt = timezone.make_aware(datetime.combine(start_date, time.min), tz)
        end_next_dt = timezone.make_aware(
            datetime.combine(end_date + timedelta(days=1), time.min), tz
        )

        qs = qs.filter(created_at__gte=start_dt, created_at__lt=end_next_dt)
        return qs.aggregate(total=Coalesce(Sum("amount"), 0))["total"]

    def get_expense(self, obj):
        request = self.context.get("request")
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        expense = (
            Finance.objects.filter(casher=obj, action="EXPENSE")
            .exclude(
                Q(kind__kind=FinanceKindTypeChoices.BONUS)
                | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
            )
            .aggregate(Sum("amount"))["amount__sum"]
            or 0
        )
        if start_date:
            start = parse_date(start_date)
            end = parse_date(end_date) if end_date else start

            from datetime import timedelta

            end = end + timedelta(days=1) - timedelta(seconds=1)

            expense = (
                Finance.objects.filter(
                    casher=obj,
                    action="EXPENSE",
                    created_at__gte=start,
                    created_at__lte=end,
                )
                .exclude(
                    Q(kind__kind=FinanceKindTypeChoices.BONUS)
                    | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
                )
                .aggregate(Sum("amount"))["amount__sum"]
                or 0
            )

        if start_date and end_date:
            expense = (
                Finance.objects.filter(
                    casher=obj,
                    action="EXPENSE",
                    created_at__gte=start_date,
                    created_at__lte=end_date,
                )
                .exclude(
                    # Q(kind__kind=FinanceKindTypeChoices.BONUS)
                    # | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
                    Q(kind__kind=FinanceKindTypeChoices.BONUS)
                    | Q(kind__kind=FinanceKindTypeChoices.MONEY_BACK)
                )
                .aggregate(Sum("amount"))["amount__sum"]
                or 0
            )

        return expense

    def create(self, validated_data):
        filial = validated_data.pop("filial", None)
        if not filial:
            request = self.context.get("request")  #
            if request and hasattr(request.user, "filial"):
                filial = request.user.filial.first()

        if not filial:
            raise serializers.ValidationError(
                {"filial": "Filial could not be determined."}
            )
        casher = Casher.objects.create(filial=filial, **validated_data)
        return casher

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserListSerializer(
            instance.user, include_only=["id", "full_name", "first_name", "last_name"]
        ).data

        return rep


class CasherHandoverSerializer(serializers.ModelSerializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    amount = serializers.IntegerField()
    casher = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    payment_method = serializers.CharField()

    class Meta:
        model = Handover
        fields = [
            "id",
            "receiver",
            "amount",
            "casher",
            "payment_method",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["receiver"] = CasherSerializer(instance.receiver).data
        rep["casher"] = CasherSerializer(instance.casher).data
        return rep


class FinanceSerializer(serializers.ModelSerializer):

    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    casher = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())

    attendance = serializers.PrimaryKeyRelatedField(
        queryset=Attendance.objects.all(),
        allow_null=True,
    )
    total = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Finance
        fields = [
            "id",
            "action",
            "casher",
            "amount",
            "kind",
            "payment_method",
            "student",
            "lid",
            "attendance",
            "stuff",
            "creator",
            "comment",
            "created_at",
            "updated_at",
            "total",
            "balance",
        ]

    def get_total(self, obj):
        # Aggregate the sum of income and outcome
        income_sum = (
            Finance.objects.filter(action="INCOME").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        outcome_sum = (
            Finance.objects.filter(action="EXPENSE").aggregate(total=Sum("amount"))[
                "total"
            ]
            or 0
        )
        # Calculate the balance
        return income_sum - outcome_sum

    def get_balance(self, obj):
        # Fetch the related CustomUser instance
        stuff = obj.stuff
        student = obj.student

        # Ensure that stuff or student is not None
        if stuff:
            income = (
                Finance.objects.filter(stuff=stuff, action="INCOME").aggregate(
                    balance=Sum("amount")
                )["balance"]
                or 0
            )
            outcome = (
                Finance.objects.filter(stuff=stuff, action="EXPENSE").aggregate(
                    balance=Sum("amount")
                )["balance"]
                or 0
            )
            return income - outcome

        # Optional: handle balance calculation for students if needed
        if student:
            income = (
                Finance.objects.filter(student=student, action="INCOME").aggregate(
                    balance=Sum("amount")
                )["balance"]
                or 0
            )
            outcome = (
                Finance.objects.filter(student=student, action="EXPENSE").aggregate(
                    balance=Sum("amount")
                )["balance"]
                or 0
            )
            return income - outcome

        # Default to 0 if neither stuff nor student exists
        return 0

    def to_internal_value(self, data):

        data["creator"] = self.context["request"].user.id

        return super(FinanceSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        # Automatically assign the creator from the request user
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["creator"] = request.user

        if request and hasattr(request.user, "filial"):
            validated_data["filial"] = request.user.filial.first()

        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if instance.lid:
            representation["lid"] = {
                "id": instance.lid.id,
                "full_name": f"{instance.lid.first_name} {instance.lid.last_name}",
            }

        representation["creator"] = (
            UserListSerializer(instance.creator, include_only=["id", "name"]).data
            if instance.creator
            else None
        )

        representation["kind"] = (
            KindSerializer(instance.kind).data if instance.kind else None
        )

        representation["student"] = (
            StudentSerializer(
                instance.student, include_only=["id", "first_name", "last_name"]
            ).data
            if instance.student
            else None
        )

        return representation


class FinanceGroupSerializer(serializers.ModelSerializer):
    summ = serializers.SerializerMethodField()

    class Meta:
        model = Finance
        fields = [
            "id",
            "casher",
            "action",
            "amount",
            "kind",
            "student",
            "lid",
            "stuff",
            "summ",
            "creator",
            "comment",
            "created_at",
        ]


class FinanceTeacherSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    casher = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    group_payments = serializers.SerializerMethodField()

    class Meta:
        model = Finance
        fields = [
            "id",
            "action",
            "casher",
            "amount",
            "kind",
            "payment_method",
            "student",
            "stuff",
            "creator",
            "comment",
            "created_at",
            "updated_at",
            "group_payments",  # New field for filtering payments by group and attendance
        ]

    def get_group_payments(self, obj):
        """Fetch attended groups, sum payments for each, and list student transactions inside."""
        teacher = obj.stuff  # Teacher related to the finance record

        # Get distinct attended groups for the teacher
        attended_groups = (
            Attendance.objects.filter(group__teacher=teacher)
            .values_list("group_id", flat=True)
            .distinct()
        )

        group_data = []

        for group_id in attended_groups:
            group_attendances = Attendance.objects.filter(group_id=group_id)

            # Sum of all payments for this group
            total_group_payment = (
                Finance.objects.filter(attendance__in=group_attendances).aggregate(
                    Sum("amount")
                )["amount__sum"]
                or 0
            )

            # Get distinct students who attended this group
            student_data = []
            students = Student.objects.filter(attendance__group_id=group_id).distinct()

            for student in students:
                student_attendances = Attendance.objects.filter(
                    group_id=group_id, student=student
                )

                # Sum total payments for this student in the group
                total_student_payment = (
                    Finance.objects.filter(
                        attendance__in=student_attendances
                    ).aggregate(Sum("amount"))["amount__sum"]
                    or 0
                )

                student_data.append(
                    {
                        "student_id": student.id,
                        "student_name": student.first_name + " " + student.last_name,
                        "total_payment": total_student_payment,
                    }
                )

            group_data.append(
                {
                    "group_id": str(
                        group_id
                    ),  # Ensure it's returned as a string (if UUID)
                    "group_name": (
                        group_attendances.first().group.name
                        if group_attendances.exists()
                        else ""
                    ),
                    "total_group_payment": total_group_payment,
                    "students": student_data,  # Ensuring unique students
                }
            )

        return group_data


class KpiFinanceSerializer(serializers.ModelSerializer):
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(), allow_null=True
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )

    class Meta:
        model = KpiFinance
        fields = [
            "id",
            "user",
            "lid",
            "student",
            "reason",
            "amount",
            "type",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = UserListSerializer(instance.user).data
        return data


class VoucherSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    number = serializers.SerializerMethodField()

    class Meta:
        model = Voucher
        fields = [
            "id",
            "creator",
            "amount",
            "number",
            "count",
            "is_expired",
            "lid",
            "student",
            "filial",
            "created_at",
        ]

    def get_number(self, obj):
        return (
            VoucherStudent.objects.filter(voucher=obj).aggregate(total=Count("id"))[
                "total"
            ]
            or 0
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["creator"] = UserListSerializer(instance.creator).data
        return data


class VoucherStudentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(), allow_null=True
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True
    )
    voucher = serializers.PrimaryKeyRelatedField(
        queryset=Voucher.objects.all(), allow_null=True
    )

    class Meta:
        model = VoucherStudent
        fields = ["id", "creator", "voucher", "lid", "student", "filial", "comment"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["creator"] = UserListSerializer(instance.creator).data
        data["voucher"] = VoucherSerializer(instance.voucher).data
        return data


class SalesSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )

    class Meta:
        model = Sale
        fields = [
            "id",
            "creator",
            "name",
            "filial",
            "amount",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["creator"] = UserListSerializer(instance.creator).data
        return data


class SaleStudentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(), allow_null=True
    )
    sale = serializers.PrimaryKeyRelatedField(
        queryset=Sale.objects.all(), allow_null=True
    )
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(), allow_null=True
    )

    class Meta:
        model = SaleStudent
        fields = [
            "id",
            "creator",
            "sale",
            "filial",
            "student",
            "group",
            "lid",
            "expire_date",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["sale"] = SalesSerializer(instance.sale).data
        data["group"] = GroupSerializer(instance.group).data
        data["creator"] = UserListSerializer(instance.creator).data
        if instance.student:
            data["student"] = StudentSerializer(instance.student).data
        if instance.lid:
            data["lid"] = LeadSerializer(instance.lid).data

        return data
