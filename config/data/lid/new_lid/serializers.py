
from rest_framework import serializers
from django.utils.module_loading import import_string
from rest_framework.generics import CreateAPIView

from .models import Lid
from ..archived.models import Archived
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...stages.models import NewLidStages
from ...stages.serializers import NewLidStageSerializer, NewOrderedLidStagesSerializer
from ...comments.models import Comment, User
from ...student.groups.models import Group
from ...student.lesson.models import Lesson
from ...tasks.models import Task


class LidSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    lid_stages = serializers.PrimaryKeyRelatedField(queryset=NewLidStages.objects.all(), allow_null=True)
    ordered_stages = serializers.PrimaryKeyRelatedField(queryset=NewLidStages.objects.all(), allow_null=True)
    call_operator  = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role='CALL_OPERATOR'), allow_null=True)

    comments = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Lid
        fields = [
            "id",
            "sender_id",
            "message_text",
            "first_name",
            "last_name",
            "phone_number",
            "date_of_birth",
            "education_lang",
            "student_type",
            "edu_class",
            "subject",
            "ball",
            "filial",
            "marketing_channel",
            "lid_stage_type",
            "ordered_stages",
            "lid_stages",
            "is_archived",
            "comments",
            "tasks",
            "call_operator",
        ]

    def get_comments(self, obj):
        comments = Comment.objects.filter(lid=obj)
        CommentSerializer = import_string("data.comments.serializers.CommentSerializer")
        return CommentSerializer(comments, many=True).data

    def get_tasks(self, obj):
        tasks = Task.objects.filter(lid=obj)
        TaskSerializer = import_string("data.tasks.serializers.TaskSerializer")
        return TaskSerializer(tasks, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(instance.marketing_channel).data if instance.marketing_channel else None
        representation['lid_stages'] = NewLidStageSerializer(instance.lid_stages).data if instance.lid_stages else None
        representation['ordered_stages'] = NewOrderedLidStagesSerializer(instance.ordered_stages).data if instance.ordered_stages else None
        representation['call_operator'] = UserSerializer(instance.call_operator).data if instance.call_operator else None

        return representation

    def update(self, instance, validated_data):
        """
        Custom update logic to assign `call_operator` if it is `None`
        and the user is a `CALL_OPERATOR`.
        """
        request = self.context['request']

        # Assign `call_operator` if it's None and the current user is a CALL_OPERATOR
        if instance.call_operator is None and request.user.role == 'CALL_OPERATOR':
            validated_data['call_operator'] = request.user

        # Update the instance using the superclass method
        instance = super().update(instance, validated_data)
        return instance


