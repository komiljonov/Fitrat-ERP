from django.db.models import Q
from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lid
from ...account.models import CustomUser
from ...account.serializers import UserSerializer
from ...comments.models import Comment
from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...student.attendance.models import Attendance
from ...student.studentgroup.models import StudentGroup
from ...tasks.models import Task


class LidSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(), allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(), allow_null=True)
    call_operator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.filter(role='CALL_OPERATOR'), allow_null=True)

    comments = serializers.SerializerMethodField()
    tasks = serializers.SerializerMethodField()
    # group = serializers.SerializerMethodField()
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
            'moderator',
            "call_operator",
            # "group",
            "lessons_count",
            "leads_count",
            "new_leads",
            "order_creating",
            "archived_new_leads",
            "created_at",
        ]

    # Filtering queryset based on request user's role and date filters
    def get_filtered_queryset(self):
        request = self.context.get('request')
        if not request:
            return Lid.objects.none()

        user = request.user
        queryset = Lid.objects.all()

        # Apply start_date and end_date filters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Apply role-based filtering
        if user.role == 'CALL_OPERATOR':
            queryset = queryset.filter(Q(call_operator=user) | Q(call_operator=None), filial=None)
        return queryset

    def get_comments(self, obj):
        comments = Comment.objects.filter(lid=obj)
        CommentSerializer = import_string("data.comments.serializers.CommentSerializer")
        return CommentSerializer(comments, many=True).data

    def get_tasks(self, obj):
        tasks = Task.objects.filter(lid=obj)
        TaskSerializer = import_string("data.tasks.serializers.TaskSerializer")
        return TaskSerializer(tasks, many=True).data
    #
    # def get_group(self, obj):
    #     groups = StudentGroup.objects.filter(lid=obj)
    #     if groups.exists():
    #         groups = [att.group for att in groups]  # Accessing the related 'group' field
    #         StudentsGroupSerializer = import_string("data.student.studentgroup.serializers.StudentsGroupSerializer")
    #         return StudentsGroupSerializer(groups, many=True).data
    #     return None

    def get_lessons_count(self, obj):
        attendance_count = Attendance.objects.filter(lid=obj, reason="IS_PRESENT").count()
        return attendance_count

    # Total leads count for this user
    def get_leads_count(self, obj):
        queryset = self.get_filtered_queryset()
        return queryset.count()

    # New leads not assigned to a filial
    def get_new_leads(self, obj):
        queryset = self.get_filtered_queryset()
        return queryset.filter(lid_stage_type="NEW_LID").count()

    # Leads in the "order creating" stage for this user
    def get_order_creating(self, obj):
        queryset = self.get_filtered_queryset()
        return queryset.filter(lid_stage_type="NEW_LID").exclude(filial=None).count()

    # Archived leads with the "new_lid" stage for this user
    def get_archived_new_leads(self, obj):
        queryset = self.get_filtered_queryset()
        return queryset.filter(is_archived=True, lid_stage_type="NEW_LID").count()

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

        if instance.call_operator is None and request.user.role == 'CALL_OPERATOR':
            validated_data['call_operator'] = request.user

        instance = super().update(instance, validated_data)
        return instance
