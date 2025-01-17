from rest_framework import serializers

from .models import File


class FileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = [
            'id',
            'file',
        ]


