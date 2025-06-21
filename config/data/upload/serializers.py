from rest_framework import serializers

from .models import File, Contract


class FileUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = File
        fields = [
            'id',
            'file',
            "choice",
            "url"
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        choice = None
        if request:
            data = request.data
            if isinstance(data, dict):
                choice = data.get("choice")

        if choice == "file":
            representation["file"] = request.build_absolute_uri(instance.file.url)

        return representation


class ContractUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = [
            'id',
            'file'

       ]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")
        if request:
            representation["file"] = request.build_absolute_uri(instance.file.url)
        return representation