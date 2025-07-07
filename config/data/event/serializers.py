from rest_framework import serializers

from .models import Event
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class EventSerializer(serializers.ModelSerializer):

    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True,allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "file",
            "photo",
            "link_preview",
            "link",
            "comment",
            "has_countdown",
            "end_date",
            "status",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)

        rep["file"] = FileUploadSerializer(instance.file,many=True,context=self.context).data
        rep["photo"] = FileUploadSerializer(instance.photo,context=self.context).data
        return rep