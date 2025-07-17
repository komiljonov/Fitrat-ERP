from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Comment, StuffComments
from ..account.models import CustomUser
from ..account.serializers import UserSerializer
from ..upload.models import File
from ..upload.serializers import FileUploadSerializer


class CommentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    photo = serializers.PrimaryKeyRelatedField(queryset=File.objects.all(),allow_null=True)
    class Meta:
        model = Comment
        fields = [
            "id",
            "creator",
            "photo",
            "lid",
            "student",
            "comment",
            "created_at",
            "updated_at",
        ]
    # def __init__(self, *args, **kwargs):
    #     # Call the parent constructor
    #
    #     # Fields you want to remove (for example, based on some condition)
    #     fields_to_remove: list | None = kwargs.pop("remove_fields", None)
    #     super(CommentSerializer, self).__init__(*args, **kwargs)
    #
    #     if fields_to_remove:
    #         # Remove the fields from the serializer
    #         for field in fields_to_remove:
    #             self.fields.pop(field, None)

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        creator = instance.creator if instance.creator else None
        rep["photo"] = FileUploadSerializer(instance.photo,context=self.context).data

        if creator:
            rep["full_name"] = f"{creator.first_name} {creator.last_name}"
            rep["first_name"] = creator.first_name
            rep["last_name"] = creator.last_name
            rep["photo"] = FileUploadSerializer(creator.photo, context=self.context).data if creator.photo else None

        return rep


class CommentStuffSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        allow_null=True,
    )
    stuff = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = StuffComments
        fields = [
            "id",
            "creator",
            "stuff",
            "comment",
            "created_at",
        ]

    def to_representation(self, instance):
        # Fetch the original representation
        rep = super().to_representation(instance)

        # Ensure the 'creator' field exists in the representation
        creator = instance.creator if instance.creator else None

        if creator:
            rep[
                "full_name"] = creator.full_name
            rep["first_name"] = creator.first_name
            rep["last_name"] = creator.last_name
            rep["photo"] = FileUploadSerializer(creator.photo, context=self.context).data if creator.photo else None

        return rep
