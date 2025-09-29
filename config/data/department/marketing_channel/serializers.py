from .models import MarketingChannel
from rest_framework import serializers


class MarketingChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MarketingChannel
        fields = "__all__"


# class Group_typeSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Group_Type
#         fields = [
#             "id",
#             "price_type",
#             "comment",
#             "created_at",
#             "updated_at",
#         ]
