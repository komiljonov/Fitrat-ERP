from rest_framework import serializers

from .models import Student


from ...department.filial.models import Filial
from ...department.filial.serializers import FilialSerializer
from ...department.marketing_channel.models import MarketingChannel
from ...department.marketing_channel.serializers import MarketingChannelSerializer
from ...stages.models import NewLidStages, StudentStages, NewStudentStages
from ...stages.serializers import StudentStagesSerializer, NewOrderedLidStagesSerializer, NewStudentStagesSerializer


class StudentSerializer(serializers.ModelSerializer):
    filial = serializers.PrimaryKeyRelatedField(queryset=Filial.objects.all(),allow_null=True)
    marketing_channel = serializers.PrimaryKeyRelatedField(queryset=MarketingChannel.objects.all(),allow_null=True)
    lid_stages = serializers.PrimaryKeyRelatedField(queryset=NewLidStages.objects.all(),allow_null=True)
    new_student_stages = serializers.PrimaryKeyRelatedField(queryset=NewLidStages.objects.all(),allow_null=True)
    active_student_stages = serializers.PrimaryKeyRelatedField(queryset=StudentStages.objects.all(),allow_null=True)

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
            "active_student_stages"
            
            "active",
            "is_archived",
        ]
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['filial'] = FilialSerializer(instance.filial).data
        representation['marketing_channel'] = MarketingChannelSerializer(instance.marketing_channel).data
        representation['lid_stages'] = NewStudentStagesSerializer(instance.new_student_stages).data
        representation['student_stages'] = StudentStagesSerializer(instance.active_student_stages).data
        return representation


