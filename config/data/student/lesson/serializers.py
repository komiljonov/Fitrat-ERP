from django.utils.module_loading import import_string
from rest_framework import serializers

from .models import Lesson
from ..attendance.models import Attendance
from ..groups.models import Group
from ..groups.serializers import GroupSerializer
from ...lid.new_lid.models import Lid
from ...lid.new_lid.serializers import LidSerializer


class LessonSerializer(serializers.ModelSerializer):
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    attendance = serializers.SerializerMethodField()
    class Meta:
        model = Lesson
        fields = [
            "id",
            'name',
            "subject",
            'group',
            'comment',
            'lesson_status',
            'lessons_count',
            'attendance',
            'created_at',
            'updated_at',
        ]

    def get_attendance(self, obj):
        attendance = Attendance.objects.filter(lesson=obj)
        AttendanceSerializer = import_string('data.student.attendance.serializers.AttendanceSerializer')
        return AttendanceSerializer(attendance, many=True).data

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['group'] = GroupSerializer(instance.group).data
        return rep

