from tokenize import group

from rest_framework import serializers

from .models import Attendance
from ..student.models import Student
from ..student.serializers import StudentSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class AttendanceSerializer(serializers.ModelSerializer):
    lid = serializers.PrimaryKeyRelatedField(queryset=Lid.objects.all())
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = Attendance
        fields = [
            'id',
            'lesson',
            'lid',
            'student',
            'teacher',
            'reason',
            'remarks',
            'created_at',
            'updated_at',
        ]

    def get_teacher(self, obj):
        teacher = (Attendance.objects.filter(student=obj.student, lesson=obj.lesson)
                   .values('lesson__group',"lesson__group__teacher__first_name", "lesson__group__teacher__last_name"))
        return teacher

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
