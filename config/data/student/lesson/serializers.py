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


class LessonScheduleSerializer(serializers.ModelSerializer):
    group_id = serializers.IntegerField(write_only=True)
    subject_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Lesson
        fields = [
            'id', 'name', 'group_id', 'subject_id', 'room_number',
            'day', 'start_time', 'end_time', 'comment', 'lesson_status', 'lessons_count'
        ]
        read_only_fields = ['id', 'lesson_status', 'lessons_count']

    def validate(self, data):
        group_id = data.get('group_id')
        room_number = data.get('room_number')
        day = data.get('day')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        # Check if group exists
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise serializers.ValidationError({"group_id": "Group not found."})
        data['group'] = group  # Attach group object for later use

        # Check for scheduling conflicts
        if Lesson.objects.filter(
            room_number=room_number,
            day=day,
            start_time__lt=end_time,  # Overlap: Starts before another lesson ends
            end_time__gt=start_time   # Overlap: Ends after another lesson starts
        ).exists():
            raise serializers.ValidationError({"schedule": "Conflict detected with an existing lesson."})

        return data

    def create(self, validated_data):
        """
        Create the lesson after validation.
        """
        group = validated_data.pop('group')
        subject_id = validated_data.pop('subject_id')

        # Create the lesson
        lesson = Lesson.objects.create(
            group=group,
            subject_id=subject_id,
            **validated_data
        )
        return lesson
