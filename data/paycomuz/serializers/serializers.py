# payments/serializers.py

from rest_framework import serializers
from decimal import Decimal

from data.paycomuz.models import Transaction


class GeneratePaymentLinkSerializer(serializers.Serializer):
    order_id = serializers.CharField(required=False, allow_null=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2,required=False, allow_null=True)
    return_url = serializers.URLField(required=False, allow_null=True)


class PaycomuzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'

