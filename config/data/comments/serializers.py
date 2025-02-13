from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Comment
from ..account.models import CustomUser
from ..account.serializers import UserSerializer
from ..upload.serializers import FileUploadSerializer

User = get_user_model()


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

    def get_creator(self, obj):
        # Fetch creator data
        creator = CustomUser.objects.filter(id=obj.creator.id).first()
        if creator:
            # Serialize the creator's photo if it exists
            return {
                "id": creator.id,
                "full_name": creator.full_name,
                "first_name": creator.first_name,
                "last_name": creator.last_name,
                "photo": FileUploadSerializer(creator.photo,context=self.context).data if creator.photo else None
            }
        return None
