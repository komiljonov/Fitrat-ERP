from rest_framework import serializers


class ClickUzSerializer(serializers.Serializer):
    click_trans_id = serializers.CharField(allow_blank=True)
    service_id = serializers.CharField(allow_blank=True)
    merchant_trans_id = serializers.CharField(allow_blank=True)
    merchant_prepare_id = serializers.CharField(allow_blank=True, required=False, allow_null=True)
    amount = serializers.CharField(allow_blank=True)
    action = serializers.CharField(allow_blank=True)
    error = serializers.CharField(allow_blank=True)
    error_note = serializers.CharField(allow_blank=True)
    sign_time = serializers.CharField()
    sign_string = serializers.CharField(allow_blank=True)
    click_paydoc_id = serializers.CharField(allow_blank=True)


from rest_framework import serializers
from ..clickuz.models import Order

class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "lid", "student", "amount", "type"]
        extra_kwargs = {
            "amount": {"required": True},
            "type": {"required": True},
        }

    def validate(self, attrs):
        if not attrs.get("lid") and not attrs.get("student"):
            raise serializers.ValidationError("Either lid or student must be provided.")
        if attrs.get("lid") and attrs.get("student"):
            raise serializers.ValidationError("Provide only one of lid or student.")
        return attrs