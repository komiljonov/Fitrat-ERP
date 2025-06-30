import icecream
from rest_framework import serializers

from .models import Archived
from ..new_lid.models import Lid
from ..new_lid.serializers import LidSerializer
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...comments.models import Comment
from ...comments.serializers import CommentSerializer
from ...student.student.models import Student
from ...student.student.serializers import StudentSerializer


class ArchivedSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)

    class Meta:
        model = Archived
        fields = [
            'id',
            'creator',
            'lid',
            'student',
            "reason",
            "comment",
            "is_archived",
            'created_at',
            'updated_at',
        ]

    def create(self, validated_data):
        request = self.context['request']
        validated_data['creator'] = request.user
        return super().create(validated_data)

    def to_representation(self, instance):
        # Get the default representation
        representation = super().to_representation(instance)

        # Add detailed serialization for related fields
        if instance.creator:
            representation['creator'] = UserSerializer(instance.creator).data
        if instance.lid:
            representation['lid'] = LidSerializer(instance.lid).data
        if instance.student:
            representation['student'] = StudentSerializer(instance.student).data
        if instance.comment:
            representation['comment'] = CommentSerializer(instance.comment).data

        # Clean the response by removing falsy values
        filtered_data = {key: value for key, value in representation.items() if value not in [{}, [], None, "", False]}
        return filtered_data



class StuffArchivedSerializer(ArchivedSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    stuff = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)
    comment = serializers.CharField(max_length=100)
    class Meta:
        model = Comment
        fields = [
            'id',
            'creator',
            'stuff',
            'comment',
            'created_at',
            'updated_at',
        ]
    def create(self, validated_data):
        comment = Comment.objects.create(
            creator=validated_data['creator'],
            comment=validated_data['comment'],
            stuff=validated_data['stuff'],
            is_archived=True,
        )
        if comment:
            icecream.ic(comment)