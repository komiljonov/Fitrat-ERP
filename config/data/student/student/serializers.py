from django.contrib.auth import authenticate
from django.utils.module_loading import import_string
from kombu.asynchronous.http import Response
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Student
from ..attendance.models import Attendance
from ..lesson.models import Lesson
from ...account.permission import PhoneAuthBackend
from ...account.serializers import UserSerializer
from ...comments.models import Comment

from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...stages.models import NewLidStages, StudentStages, NewStudentStages
from ...stages.serializers import StudentStagesSerializer, NewOrderedLidStagesSerializer, NewStudentStagesSerializer
from ...tasks.models import Task


class StudentSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(),allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(),allow_null=True)
    new_student_stages = serializers.PrimaryKeyRelatedField(queryset=NewStudentStages.objects.all(),allow_null=True)
    active_student_stages = serializers.PrimaryKeyRelatedField(queryset=StudentStages.objects.all(),allow_null=True)
    comments = serializers.SerializerMethodField()

    tasks = serializers.SerializerMethodField()

    group = serializers.SerializerMethodField()


    password  = serializers.CharField(write_only=True)

    attendance_count = serializers.SerializerMethodField()
    class Meta:
        model = Student
        fields = [
            'id',
            "first_name",
            "last_name",
            "phone",
            'password',
            "date_of_birth",
            "education_lang",
            "student_type",
            "edu_class",
            "subject",
            "ball",
            "filial",
            "marketing_channel",

            "comments",
            "group",

            "tasks",

            "student_stage_type",
            "new_student_stages",
            "active_student_stages",

            'balance_status',
            'balance',

            'moderator',

            'call_operator',

            "is_archived",

            "attendance_count",
        ]


    def get_comments(self, obj):
        comments = Comment.objects.filter(student=obj)
        CommentSerializer = import_string("data.comments.serializers.CommentSerializer")
        return CommentSerializer(comments, many=True).data



    def get_tasks(self, obj):
        tasks = Task.objects.filter(student=obj)
        TaskSerializer = import_string("data.tasks.serializers.TaskSerializer")
        return TaskSerializer(tasks, many=True).data

    def get_group(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        if attendance.exists():
            groups = [att.lesson.group for att in attendance]
            GroupSerializer = import_string("data.student.groups.serializers.GroupSerializer")
            return GroupSerializer(groups, many=True).data
        return None

    def get_attendance_count(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        return attendance.count() + 1

    def update(self, instance, validated_data):
        if validated_data.get('password'):
            password = validated_data.get('password')
            instance.set_password(password)
            instance.save()


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None


        representation['moderator'] = UserSerializer(instance.moderator).data if instance.moderator else None
        # Safely handle new_student_stages
        if isinstance(instance.new_student_stages, NewStudentStages):
            representation['new_student_stages'] = NewStudentStagesSerializer(instance.new_student_stages).data
        else:
            representation['new_student_stages'] = None

        # # Safely handle active_student_stages
        if isinstance(instance.active_student_stages, StudentStages):
            representation['active_student_stages'] = StudentStagesSerializer(instance.active_student_stages).data
        else:
            representation['active_student_stages'] = None

        return representation




class StudentTokenObtainPairSerializer(TokenObtainPairSerializer):
    phone = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        phone = attrs.get('phone')
        password = attrs.get('password')

        if phone and password:
            backend = PhoneAuthBackend()
            user = backend.authenticate(
                request=self.context.get('request'),
                phone=phone,
                password=password,
            )

            if not user:
                raise serializers.ValidationError(
                    "Unable to log in with provided credentials.",
                    code="authorization"
                )
        else:
            raise serializers.ValidationError(
                "Must include 'phone' and 'password'.",
                code="authorization"
            )

        attrs['user'] = user
        return attrs