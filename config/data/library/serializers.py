from rest_framework import serializers

from .models import LibraryCategory,Library
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer
# import fitz
# from django.core.files.base import ContentFile
# from io import BytesIO
# from PIL import Image
# import uuid

class LibraryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryCategory
        fields = [
            "id",
            "name",
            "created_at",
        ]


class LibrarySerializer(serializers.ModelSerializer):
    book = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), allow_null=False)
    file = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(), many=True, allow_null=False)
    category = serializers.PrimaryKeyRelatedField(queryset=LibraryCategory.objects.all(), allow_null=False)

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
            "cover",
            "file",
            "created_at",
        ]

    # def create(self, validated_data):
    #     book_file = validated_data.get("book")
    #
    #     pdf_path = book_file.file.path
    #     doc = fitz.open(pdf_path)
    #     page = doc.load_page(0)
    #
    #     pix = page.get_pixmap(dpi=150)
    #     image_bytes = pix.tobytes("png")
    #
    #     image_file = ContentFile(image_bytes)
    #     image_name = f"{uuid.uuid4()}.png"
    #
    #     cover_file = File.objects.create(
    #         file=image_file,
    #         name=image_name
    #     )
    #
    #     validated_data["cover"] = cover_file

        # return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["category"] = LibraryCategorySerializer(instance.category).data
        rep["book"] = FileUploadSerializer(instance.book, context=self.context).data
        rep["file"] = FileUploadSerializer(instance.file, many=True, context=self.context).data
        rep["cover"] = FileUploadSerializer(instance.cover, context=self.context).data if instance.cover else None
        return rep