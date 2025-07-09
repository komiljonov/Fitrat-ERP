# payments/serializers.py

from rest_framework import serializers
from decimal import Decimal

class GeneratePaymentLinkSerializer(serializers.Serializer):
    order_id = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    return_url = serializers.URLField()
