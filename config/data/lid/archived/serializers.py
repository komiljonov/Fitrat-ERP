import icecream
from rest_framework import serializers
from django.utils import timezone

from .models import Archived, Frozen
from data.lid.new_lid.models import Lid
from data.lid.new_lid.serializers import LeadSerializer
from data.account.models import CustomUser
from data.account.serializers import UserSerializer
from data.comments.models import Comment
from data.comments.serializers import CommentSerializer
from data.student.student.models import Student
from data.student.student.serializers import StudentSerializer


class ArchivedSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())

    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = Archived
        fields = [
            "id",
            "creator",
            "lid",
            "student",
            "reason",
            "comment",
            "is_archived",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]
        validated_data["creator"] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)

        # Add detailed serialization for related fields
        if instance.creator:
            representation["creator"] = UserSerializer(
                instance.creator,
                include_only=["id", "first_name", "last_name", "middle_name"],
            ).data

        if instance.lid:
            representation["lid"] = LeadSerializer(
                instance.lid,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone_number",
                    "sales_manager",
                    "service_manager",
                    "lid_stage_type",
                    "lid_stages",
                    "ordered_stages",
                    "call_operator",
                ],
            ).data

        if instance.student:
            representation["student"] = StudentSerializer(
                instance.student,
                include_only=[
                    "id",
                    "first_name",
                    "last_name",
                    "middle_name",
                    "phone",
                    "balance",
                    "sales_manager",
                    "service_manager",
                    "student_stage_type",
                    "new_student_stages",
                ],
            ).data

        if instance.comment:
            representation["comment"] = CommentSerializer(instance.comment).data

        # Clean the response by removing falsy values
        filtered_data = {
            key: value
            for key, value in representation.items()
            if value not in [{}, [], None, "", False]
        }
        return filtered_data


class StuffArchivedSerializer(ArchivedSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    stuff = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(), allow_null=True
    )
    comment = serializers.CharField(max_length=100)

    class Meta:
        model = Comment
        fields = [
            "id",
            "creator",
            "stuff",
            "comment",
            "created_at",
            "updated_at",
        ]

    def create(self, validated_data):
        comment = Comment.objects.create(
            creator=validated_data["creator"],
            comment=validated_data["comment"],
            stuff=validated_data["stuff"],
            is_archived=True,
        )
        if comment:
            icecream.ic(comment)


class FrozenSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        allow_null=True,
    )
    lid = serializers.PrimaryKeyRelatedField(
        queryset=Lid.objects.all(),
        allow_null=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        allow_null=True,
    )

    class Meta:
        model = Frozen

        fields = [
            "id",
            "creator",
            "lid",
            "student",
            "reason",
            "comment",
            "is_frozen",
            "archived_at",
            "created_at",
        ]

    def create(self, validated_data):
        request = self.context["request"]

        validated_data["creator"] = request.user

        if validated_data["is_archived"]:
            validated_data["archived_at"] = timezone.now()

        return super().create(validated_data)

    def to_representation(self, instance):

        representation = super().to_representation(instance)

        # Add detailed serialization for related fields
        if instance.creator:
            representation["creator"] = UserSerializer(instance.creator).data

        if instance.lid:
            representation["lid"] = LeadSerializer(instance.lid).data

        if instance.student:
            representation["student"] = StudentSerializer(instance.student).data

        if instance.comment:
            representation["comment"] = CommentSerializer(instance.comment).data

        # Clean the response by removing falsy values
        filtered_data = {
            key: value
            for key, value in representation.items()
            if value not in [{}, [], None, "", False]
        }

        return filtered_data
