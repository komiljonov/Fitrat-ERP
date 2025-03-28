from rest_framework import serializers
from .models import Homework
from ..subject.models import Theme
from ..subject.serializers import ThemeSerializer
from ...upload.models import File
from ...upload.serializers import FileUploadSerializer


class HomeworkSerializer(serializers.ModelSerializer):
    theme = serializers.PrimaryKeyRelatedField(queryset=Theme.objects.all(),
                                               allow_null=True)
    video = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),
                                              allow_null=True)
    document = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),
                                                  allow_null=True)
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),
                                               allow_null=True)

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
        res["theme"] = ThemeSerializer(instance.theme).data
        res["video"] = FileUploadSerializer(instance.video).data
        res["documents"] = FileUploadSerializer(instance.documents).data
        res["photo"] = FileUploadSerializer(instance.photo).data
        return res
