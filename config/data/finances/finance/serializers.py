from django.contrib.admin import action
from django.db.models import Sum
from rest_framework import serializers

from .models import Finance
from data.account.models import CustomUser
from data.account.serializers import UserListSerializer
from data.student.student.models import Student


class FinanceSerializer(serializers.ModelSerializer):
    # Automatically assign `creator` from the request user
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    balance = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()


    class Meta:
        model = Finance
        fields = [
            'id',
            'action',
            'amount',
            'kind',
            'student',
            'stuff',
            'balance',
            'total',
            'creator',
            'comment',
            'created_at',
            'updated_at',
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
        return representation
