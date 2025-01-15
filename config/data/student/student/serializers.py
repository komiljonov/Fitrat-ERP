from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Student
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
    new_student_stages = serializers.PrimaryKeyRelatedField(queryset=NewLidStages.objects.all(),allow_null=True)
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
        group = Lesson.objects.filter(student=obj)
        LessonSerializer = import_string("data.student.lesson.serializers.LessonSerializer")
        return LessonSerializer(group, many=True).data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['filial'] = FilialSerializer(instance.filial).data
        representation['marketing_channel'] = MarketingChannelSerializer(instance.marketing_channel).data
        representation['new_student_stages'] = NewStudentStagesSerializer(instance.new_student_stages).data
        representation['active_student_stages'] = StudentStagesSerializer(instance.active_student_stages).data
        return representation


