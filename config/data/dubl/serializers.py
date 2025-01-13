from rest_framework import serializers
from .models import Dubl
from ..command.models import TimeStampModel
from ..lid.new_lid.serializers import LidSerializer
from ..student.student.models import Student
from ..lid.new_lid.models import Lid

class DublSerializer(serializers.ModelSerializer):  # Use ModelSerializer
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())

    class Meta:
        model = Dubl
        fields = [
            "id",
            "student",
            "lid",
            "is_okay",
            "on_merge",
            "message",
            "created_at",
            "updated_at",
        ]

    def to_representation(self, instance):
        # Use the default representation and customize it
        representation = super().to_representation(instance)
        representation["lid"] = LidSerializer(instance.lid).data  # Add nested serialization for `lid`
        return representation
