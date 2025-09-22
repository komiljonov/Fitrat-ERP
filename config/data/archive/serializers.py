from rest_framework import serializers

from data.archive.models import Archive


class ArchiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Archive

        fields = "__all__"
