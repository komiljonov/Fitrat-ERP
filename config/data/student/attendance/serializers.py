from rest_framework import serializers

from .models import Attendance
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())

    class Meta:
        model = Attendance
        fields = [
            'id',
            'lesson',
            'lid',
            'student',
            'reason',
            'remarks',
        ]

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        if instance.lid:
            rep['lid'] = LidSerializer(instance.lid).data
        else:
            rep.pop('lid', None)

        if instance.student:
            rep['student'] = StudentSerializer(instance.student).data
        else:
            rep.pop('student', None)

        filtered_data = {key: value for key, value in rep.items() if value not in [{}, [], None, "", False]}
        return filtered_data
