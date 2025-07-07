from rest_framework import serializers

from .models import LibraryCategory,Library
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class LibraryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCategory
        fields = [
            "id",
            "name",
            "created_at",
        ]


class LibrarySerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=False)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),many=True,allow_null=False)
    class Meta:
        model = Library
        fields = [
            "id",
            "category",
            "name",
            "choice",
            "description",
            "title",
            "author",
            "book",
            "file",
            "created_at",
        ]
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["book"] = FileUploadSerializer(instance.book,context=self.context).data
        rep["file"] = FileUploadSerializer(instance.file,many=True,context=self.context).data

        return rep