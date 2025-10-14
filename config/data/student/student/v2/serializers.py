from rest_framework import serializers


class StudentFreezeSerializer(serializers.Serializer):
    frozen_reason = serializers.CharField(required=True)
    frozen_till_date = serializers.DateField(required=True)