from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Comment
from ..account.models import CustomUser
from ..account.serializers import UserSerializer
from ..upload.serializers import FileUploadSerializer


class CommentSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    class Meta:
        model = Comment
        fields = [
            "id",
            "creator",
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
        # Fetch the original representation
        rep = super().to_representation(instance)

        # Ensure the 'creator' field exists in the representation
        creator = instance.creator if instance.creator else None

        if creator:
            rep[
                "full_name"] = f"{creator.first_name} {creator.last_name}"  # You can combine first and last name if desired
            rep["first_name"] = creator.first_name
            rep["last_name"] = creator.last_name
            rep["photo"] = FileUploadSerializer(creator.photo, context=self.context).data if creator.photo else None

        return rep
