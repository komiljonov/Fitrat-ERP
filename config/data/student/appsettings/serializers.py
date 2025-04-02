
from rest_framework import serializers

from .models import Store
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class StoresSerializer(serializers.ModelSerializer):
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=True)

    class Meta:
        model = Store
        fields = [
            "id",
            "video",
            "seen",
            "created_at",
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["video"] = FileUploadSerializer(instance.video, context=self.context).data
        return rep