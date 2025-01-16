from rest_framework.serializers import ModelSerializer
from .models import NewLidStages, NewStudentStages, NewOredersStages, StudentStages


class NewLidStageSerializer(ModelSerializer):
    class Meta:
        model = NewLidStages
        fields = '__all__'


class NewOrderedLidStagesSerializer(ModelSerializer):
    class Meta:
        model = NewOredersStages
        fields = '__all__'


class StudentStagesSerializer(ModelSerializer):
    class Meta:
        model = StudentStages
        fields = '__all__'


class NewStudentStagesSerializer(ModelSerializer):
    class Meta:
        model = NewStudentStages
        fields = '__all__'
