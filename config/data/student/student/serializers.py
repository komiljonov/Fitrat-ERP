from django.utils.module_loading import import_string
from kombu.asynchronous.http import Response
from rest_framework import serializers

from .models import Student
from ..attendance.models import Attendance
from ..lesson.models import Lesson

from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...stages.models import NewLidStages, StudentStages, NewStudentStages
from ...stages.serializers import StudentStagesSerializer, NewOrderedLidStagesSerializer, NewStudentStagesSerializer

class StudentSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(),allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(),allow_null=True)
    new_student_stages = serializers.PrimaryKeyRelatedField(queryset=NewStudentStages.objects.all(),allow_null=True)
    active_student_stages = serializers.PrimaryKeyRelatedField(queryset=StudentStages.objects.all(),allow_null=True)
    group = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id',
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

            "student_stage_type",
            "new_student_stages",
            "active_student_stages",

            "group",

            "is_archived",
        ]

    def get_group(self, obj):
        attendance = Attendance.objects.filter(student=obj)
        if attendance.exists():
            groups = [att.lesson.group for att in attendance]
            GroupSerializer = import_string("data.student.groups.serializers.GroupSerializer")
            return GroupSerializer(groups, many=True).data
        return None


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['filial'] = FilialSerializer(instance.filial).data if instance.filial else None
        representation['marketing_channel'] = MarketingChannelSerializer(
            instance.marketing_channel).data if instance.marketing_channel else None

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



