from django.contrib.admin import action
from django.db.models import Sum
from rest_framework import serializers

from .models import Finance, Casher, Handover, Kind, PaymentMethod
from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.student.student.models import Student
from ...student.attendance.models import Attendance

class KindSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kind
        fields = [
            'id',
            'name',
            'action',
            'color',
            'created_at',
        ]

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = [
            'id',
            'name',
        ]


class CasherSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    balance = serializers.SerializerMethodField()
    income = serializers.SerializerMethodField()
    expense = serializers.SerializerMethodField()

    class Meta:
        model = Casher
        fields = [
            'id',
            'name',
            'user',
            'role',
            'balance',
            'income',
            'expense',
        ]

    def get_balance(self, obj):
        income = Finance.objects.filter(casher=obj, action='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = Finance.objects.filter(casher=obj, action='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0
        return income - expense

    def get_income(self, obj):
        return Finance.objects.filter(casher=obj, action='INCOME').aggregate(Sum('amount'))['amount__sum'] or 0

    def get_expense(self, obj):
        return Finance.objects.filter(casher=obj, action='EXPENSE').aggregate(Sum('amount'))['amount__sum'] or 0

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["user"] = UserListSerializer(instance.user).data
        return rep


class CasherHandoverSerializer(serializers.ModelSerializer):
    receiver = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    amount = serializers.IntegerField()
    casher = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    class Meta:
        model = Handover
        fields = [
            'id',
            'receiver',
            'amount',
            'casher',
            'created_at',
            'updated_at',
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["receiver"] = CasherSerializer(instance.receiver).data
        rep["casher"] = CasherSerializer(instance.casher).data
        return rep


class FinanceSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    casher = serializers.PrimaryKeyRelatedField(queryset=Casher.objects.all())
    attendance = serializers.PrimaryKeyRelatedField(queryset=Attendance.objects.all(),allow_null=True)
    total = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()

    class Meta:
        model = Finance
        fields = [
            'id',
            'action',
            'casher',
            'amount',
            'kind',
            'payment_method',
            'student',
            'attendance',
            'stuff',
            'creator',
            'comment',
            'created_at',
            'updated_at',
            'total',
            'balance',
        ]

    def get_total(self, obj):
        # Aggregate the sum of income and outcome
        income_sum = Finance.objects.filter(action='INCOME').aggregate(total=Sum('amount'))['total'] or 0
        outcome_sum = Finance.objects.filter(action='EXPENSE').aggregate(total=Sum('amount'))['total'] or 0
        # Calculate the balance
        return income_sum - outcome_sum

    def get_balance(self, obj):
        # Fetch the related CustomUser instance
        stuff = obj.stuff
        student = obj.student

        # Ensure that stuff or student is not None
        if stuff:
            income = Finance.objects.filter(stuff=stuff, action="INCOME").aggregate(balance=Sum('amount'))[
                         'balance'] or 0
            outcome = Finance.objects.filter(stuff=stuff, action="EXPENSE").aggregate(balance=Sum('amount'))[
                          'balance'] or 0
            return income - outcome

        # Optional: handle balance calculation for students if needed
        if student:
            income = Finance.objects.filter(student=student, action="INCOME").aggregate(balance=Sum('amount'))[
                         'balance'] or 0
            outcome = Finance.objects.filter(student=student, action="EXPENSE").aggregate(balance=Sum('amount'))[
                          'balance'] or 0
            return income - outcome

        # Default to 0 if neither stuff nor student exists
        return 0

    def to_internal_value(self, data):

        data['creator'] = self.context['request'].user.id

        return super(FinanceSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        # Automatically assign the creator from the request user
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['creator'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        # Use the `UserListSerializer` to serialize the creator field
        representation["creator"] = UserListSerializer(instance.creator).data
        representation['kind'] = KindSerializer(instance.kind).data
        representation['payment_method'] = PaymentMethodSerializer(instance.payment_method).data
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
            'id',
            'action',
            'casher',
            'amount',
            'kind',
            'payment_method',
            'student',
            'stuff',
            'creator',
            'comment',
            'created_at',
            'updated_at',
            'group_payments',  # New field for filtering payments by group and attendance
        ]

    def get_group_payments(self, obj):
        """Fetch attended groups, sum payments for each, and list student transactions inside."""
        teacher = obj.stuff  # Teacher related to the finance record

        # Get distinct attended groups for the teacher
        attended_groups = Attendance.objects.filter(group__teacher=teacher).values_list('group_id', flat=True).distinct()

        group_data = []

        for group_id in attended_groups:
            group_attendances = Attendance.objects.filter(group_id=group_id)

            # Sum of all payments for this group
            total_group_payment = Finance.objects.filter(attendance__in=group_attendances).aggregate(
                Sum('amount'))['amount__sum'] or 0

            # Get distinct students who attended this group
            student_data = []
            students = Student.objects.filter(attendance__group_id=group_id).distinct()

            for student in students:
                student_attendances = Attendance.objects.filter(group_id=group_id, student=student)

                # Sum total payments for this student in the group
                total_student_payment = Finance.objects.filter(attendance__in=student_attendances).aggregate(
                    Sum('amount'))['amount__sum'] or 0

                student_data.append({
                    "student_id": student.id,
                    "student_name": student.first_name + " " + student.last_name,
                    "total_payment": total_student_payment
                })

            group_data.append({
                "group_id": str(group_id),  # Ensure it's returned as a string (if UUID)
                "group_name": group_attendances.first().group.name if group_attendances.exists() else "",
                "total_group_payment": total_group_payment,
                "students": student_data  # Ensuring unique students
            })

        return group_data