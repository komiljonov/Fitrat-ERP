from django.db.models import Q
from redis.commands.search.reducers import count
from rest_framework import serializers
from django.utils.module_loading import import_string
from rest_framework.generics import CreateAPIView

from .models import Lid
from icecream import ic
from ..archived.models import Archived
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...stages.models import NewLidStages, NewOredersStages
from ...stages.serializers import NewLidStageSerializer, NewOrderedLidStagesSerializer
from ...comments.models import Comment
from ...student.attendance.models import Attendance
from ...tasks.models import Task


class LidSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    call_operator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='CALL_OPERATOR'), allow_null=True)

    comments = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    # Statistical fields
    leads_count = serializers.SerializerMethodField()
    new_leads = serializers.SerializerMethodField()
    order_creating = serializers.SerializerMethodField()
    archived_new_leads = serializers.SerializerMethodField()

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
            "group",
            "lessons_count",
            "leads_count",
            "new_leads",
            "order_creating",
            "archived_new_leads",
            "created_at",
        ]

    def get_comments(self, obj):
        comments = Comment.objects.filter(lid=obj)
        CommentSerializer = import_string("data.comments.serializers.CommentSerializer")
        return CommentSerializer(comments, many=True).data

    def get_tasks(self, obj):
        tasks = Task.objects.filter(lid=obj)
        TaskSerializer = import_string("data.tasks.serializers.TaskSerializer")
        return TaskSerializer(tasks, many=True).data

    def get_group(self, obj):
        attendance = Attendance.objects.filter(lid=obj)
        if attendance.exists():
            groups = [att.lesson.group for att in attendance]
            GroupSerializer = import_string("data.student.groups.serializers.GroupSerializer")
            return GroupSerializer(groups, many=True).data
        return None

    def get_lessons_count(self, obj):
        attendance_count = Attendance.objects.filter(lid=obj, reason="IS_PRESENT").count()
        return attendance_count

    # Total leads count for this user
    def get_leads_count(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user

            return Lid.objects.filter(Q(call_operator=user) |Q( call_operator=None) , filial=None).count()
        return 0

    # New leads not assigned to a filial
    def get_new_leads(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return Lid.objects.filter(call_operator=user, filial=None, lid_stage_type="NEW_LID").count()
        return 0

    # Leads in the "order creating" stage for this user
    def get_order_creating(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return Lid.objects.filter(
                call_operator=user,
                filial=None,
                lid_stage_type="NEW_LID"
            ).count()
        return 0

    # Archived leads with the "new_lid" stage for this user
    def get_archived_new_leads(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            return Lid.objects.filter(call_operator=user, is_archived=True, lid_stage_type="NEW_LID").count()
        return 0

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(instance.marketing_channel).data if instance.marketing_channel else None
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
