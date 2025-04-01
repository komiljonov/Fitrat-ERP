from rest_framework import serializers
from .models import Homework
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class HomeworkSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(), allow_null=True)
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    documents = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=True)

    class Meta:
        model = Homework
        fields = [
            "id",
            "title",
            "body",
            "theme",
            "video",
            "documents",
            "photo",
            "created_at"
        ]

    def to_representation(self, instance):
        res = super().to_representation(instance)
        res["theme"] = ThemeSerializer(instance.theme, context=self.context).data if instance.theme else None
        res["video"] = FileUploadSerializer(instance.video.all(), many=True,context=self.context).data
        res["documents"] = FileUploadSerializer(instance.documents.all(), many=True,context=self.context).data
        res["photo"] = FileUploadSerializer(instance.photo.all(), many=True,context=self.context).data
        return res

