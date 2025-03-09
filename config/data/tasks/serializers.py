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

        # ✅ Get 'filial' from validated_data
        filial = validated_data.get('filial')

        # ✅ If 'filial' is None, try to get from performer's filial (ManyToManyField)
        if filial is None:
            performer = validated_data.get('performer')  # Get performer instance

            if performer:
                performer_filials = performer.filial.all()  # Get all related filials
                ic(performer_filials)

                if performer_filials.exists():
                    validated_data['filial'] = performer_filials.first()  # ✅ Assign Filial instance, not ID
                else:
                    raise serializers.ValidationError({"filial": "Filial is required but cannot be determined."})
            else:
                raise serializers.ValidationError({"filial": "Filial is required but missing."})

        validated_data['creator'] = request.user
        return super().create(validated_data)

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

