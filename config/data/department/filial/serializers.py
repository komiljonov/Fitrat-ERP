from rest_framework import serializers

from .models import Filial
from data.account.models import CustomUser
from data.command.models import UserFilial


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = ["id", "name"]


class UserFilialSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(
        queryset=Filial.objects.all(),
        allow_null=True,
    )
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = UserFilial
        fields = [
            "id",
            "filial",
            "user",
            "is_archived",
            "created_at",
        ]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["filial"] = FilialSerializer(instance.filial).data
        ret["user"] = {
            "id": instance.user.id,
            "full_name": instance.user.full_name,
            "phone": instance.user.phone,
        }

        return ret
