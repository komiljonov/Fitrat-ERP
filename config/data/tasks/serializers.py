from django.contrib.auth import get_user_model
from icecream import ic
from rest_framework import serializers

from ..account.models import CustomUser
from ..lid.new_lid.models import Lid
from ..lid.new_lid.serializers import LidSerializer
from ..student.student.models import Student
from ..student.student.serializers import StudentSerializer
from ..tasks.models import Task
from ..account.serializers import UserListSerializer



class TaskSerializer(serializers.ModelSerializer):
    creator = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all(), allow_null=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), allow_null=True)
    performer = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), allow_null=True)

    class Meta:
        model = Task
        fields = [
            "id",
            "creator",
            'lid',
            'student',
            'performer',
            "filial",
            "task",
            "comment",
            "date_of_expired",
            "status",
            "created_at",
            "updated_at",
        ]

    def to_internal_value(self, data):

        data['creator'] = self.context['request'].user.id

        return super(TaskSerializer, self).to_internal_value(data)

    def create(self, validated_data):
        request = self.context['request']
        filial = validated_data.pop('filial', None)

        performer = validated_data.get('performer')
        lid = validated_data.get('lid')
        student = validated_data.get('student')

        if isinstance(performer, int):
            performer = CustomUser.objects.filter(id=performer).first()
            validated_data['performer'] = performer

        if isinstance(lid, int):
            lid = Lid.objects.filter(id=lid).first()
            validated_data['lid'] = lid

        if isinstance(student, int):
            student = Student.objects.filter(id=student).first()
            validated_data['student'] = student

        if filial is None and performer:
            performer_filials = performer.filial.all()
            if performer_filials.exists():
                filial = performer_filials.first()
            else:
                raise serializers.ValidationError({"filial": "Filial is required but cannot be determined."})

        valid_task_fields = {field.name for field in Task._meta.fields}
        validated_data = {key: value for key, value in validated_data.items() if key in valid_task_fields}

        validated_data['creator'] = request.user
        task = super().create(validated_data)

        if filial:
            task.filial.set([filial])

        return task

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["creator"] = UserListSerializer(instance.creator,context=self.context).data
        representation['performer'] = UserListSerializer(instance.performer,context=self.context).data
        # Corrected the syntax for `UserListSerializer`

        if instance.lid:
            representation['lid'] = LidSerializer(instance.lid).data

        else:
            representation.pop('lid', None)

        if instance.student:
            representation['student'] = StudentSerializer(instance.student).data

        else:
            representation.pop('student', None)

        # Filter out unwanted values
        filtered_data = {key: value for key, value in representation.items() if value not in [{}, [], None, "", False]}
        return filtered_data

